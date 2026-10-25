/* IDES administrative events and clocks. No diagnosis, eligibility or outcome engine. */
(function(global){
'use strict';
var DAY=86400000;
function parse(value){if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(value))return null;var d=new Date(value+'T00:00:00Z'),t=d.getTime();return Number.isFinite(t)&&d.toISOString().slice(0,10)===value?t:null;}
function iso(t){return t==null?null:new Date(t).toISOString().slice(0,10);}
function months(t,n){if(t==null)return null;var d=new Date(t),y=d.getUTCFullYear(),m=d.getUTCMonth()+n,day=d.getUTCDate(),last=new Date(Date.UTC(y,m+1,0)).getUTCDate();return day>last?null:Date.UTC(y,m,day);}
function copy(x){return JSON.parse(JSON.stringify(x));}
// Navy/DoD default only. VA clocks keep their own authority and helper.
function federalWorkday(t){
 var d=new Date(t),y=d.getUTCFullYear(),weekday=d.getUTCDay();if(weekday===0||weekday===6)return false;
 function nth(yr,m,w,n){var first=Date.UTC(yr,m,1);return first+((w-new Date(first).getUTCDay()+7)%7+(n-1)*7)*DAY;}
 function observed(yr,m,day){var v=Date.UTC(yr,m,day),w=new Date(v).getUTCDay();return v+(w===6?-1:w===0?1:0)*DAY;}
 for(var yr=y-1;yr<=y+1;yr++){
  var holidays=[observed(yr,0,1),nth(yr,0,1,3),nth(yr,1,1,3),nth(yr,8,1,1),nth(yr,9,1,2),observed(yr,6,4),observed(yr,10,11),nth(yr,10,4,4),observed(yr,11,25)];
  var lastMay=Date.UTC(yr,5,0);holidays.push(lastMay-((new Date(lastMay).getUTCDay()+6)%7)*DAY);
  if(yr>=2021)holidays.push(observed(yr,5,19));if(holidays.includes(t))return false;
 }
 return true;
}
function grossEstimate(input){
 function number(key,max,integer){var raw=input[key];if(raw==null||raw==='')throw Error('Enter every amount and service input.');var n=Number(raw);if(!Number.isFinite(n)||n<0||n>max||(integer&&!Number.isInteger(n)))throw Error('Check your amounts, full years and additional months.');return n;}
 var basic=number('basicPay',1000000),base=number('retiredBase',1000000),years=number('years',100,true),months=number('months',11,true),rating=number('rating',100);
 if(!['legacy','brs'].includes(input.system)||!['pdrl','tdrl'].includes(input.status)||!['standard','combat'].includes(input.minimum))throw Error('Choose each retirement and severance assumption.');
 var credit=years+months/12,rate=input.system==='brs'?0.02:0.025,disability=base*Math.min(rating/100,0.75),longevity=base*credit*rate,floor=input.status==='tdrl'?base*0.5:0;
 var rounded=Math.min(19,Math.max(input.minimum==='combat'?6:3,years+(months>=6?1:0))),gross=Math.max(disability,longevity,floor),method=floor>Math.max(disability,longevity)?'TDRL minimum':disability===longevity?'Equal methods':longevity>disability?'Longevity method':'Disability method';
 return{disability:disability,longevity:longevity,tdrlFloor:floor,retiredGross:gross,method:method,severanceYears:rounded,severanceGross:2*basic*rounded,credit:credit,rate:rate};
}
function create(data){
 var byId={},byItem={},events=data.events;
 data.requirements.forEach(function(r){byId[r.id]=r;r.items.forEach(function(id){(byItem[id]||(byItem[id]=[])).push(r);});});
 function initial(){return{schemaVersion:1,caseId:'case-1',cycleId:'cycle-1',stage:'inquiry',stageConfirmed:false,outcome:'unknown',events:{},selectedEvents:{},branchConfirmations:{},calendarConfirmations:{},projections:{}};}
 function eventError(state,type,e,today){
  var spec=events[type];if(!spec||!e||e.eventType!==type)return'Choose a recognized event.';
  if(!e.occurrenceId||!e.caseId||e.caseId!==state.caseId)return'This event belongs to another case.';
  if(e.selectedForBranch!==(spec.repeatable?state.cycleId:state.caseId))return'Confirm the event for this case or review cycle.';
  var t=parse(e.date);if(t==null)return'Enter a valid local calendar date.';
  if(!spec.classifications.includes(e.classification))return'This event needs its own actual or issued date.';
  if(e.classification==='actual'&&(parse(today)==null||t>parse(today)))return'An actual event cannot be in the future.';
  if(e.status!=='confirmed'||e.confirmedBy!=='Marine'||!Number.isFinite(Date.parse(e.confirmedAt)))return'Confirm what happened and the source of the date.';
  if(!['notice_received','office_confirmation','issued_order','letter_date_presumption'].includes(e.confirmationBasis))return'Choose the basis for this date.';
  if(e.confirmationBasis==='letter_date_presumption'&&type!=='va_final_notice_mailed')return'The letter-date presumption applies only to VA mailing.';
  if(spec.officeRequired&&e.officeConfirmed!==true)return'Ask the named office to confirm this fact first.';
  if(e.verifierOffice!==spec.office)return'Confirm the date with the named office.';
  if(spec.repeatable&&(!e.noticeId||!/^[A-Za-z0-9_-]{1,40}$/.test(e.noticeId)))return'Add a short local notice or appointment label.';
  if(e.time){if(!/^([01]\d|2[0-3]):[0-5]\d$/.test(e.time)||!e.timezone)return'Add the appointment time and timezone.';try{new Intl.DateTimeFormat('en-US',{timeZone:e.timezone});}catch(_){return'Choose a valid appointment timezone.';}}
  return'';
 }
 function selectedId(state,rid,key){var rows=Object.values(state.selectedEvents?.[rid]?.[key]||{}).filter(function(x){return x.status==='confirmed';});return rows.length===1?rows[0].occurrenceId:null;}
 function selected(state,rid,key,type,today){
  var id=selectedId(state,rid,key),e=id&&state.events?.[type]?.[id];
  return e&&!eventError(state,type,e,today)?e:null;
 }
 function values(value){return Array.isArray(value)?value:Object.keys(value||{}).filter(function(k){return value[k]===true;});}
 function confirmation(state,field,id){var entry=state[field]?.[id],history=entry?.occurrences;return history&&Object.values(history).filter(function(x){return x.status==='confirmed';}).length!==1?null:entry;}
 function calendar(state,id,year){var c=confirmation(state,'calendarConfirmations',id);return c&&c.id===id&&c.confirmedByMarine===true&&c.officeConfirmed===true&&c.sourceUrl?.startsWith('https://')&&c.version&&Number.isFinite(Date.parse(c.confirmedAt))&&values(c.years).map(Number).includes(year)&&values(c.workdays).length&&values(c.workdays).map(Number).every(function(n){return Number.isInteger(n)&&n>=0&&n<=6;})&&values(c.holidays).every(function(d){return parse(d)!=null;})?c:null;}
 function workday(state,id,t){var c=calendar(state,id,new Date(t).getUTCFullYear());if(!c)return /^NAVY_|^DOD_/.test(id||'')&&!state.calendarConfirmations?.[id]?federalWorkday(t):null;var day=iso(t);if(c.exceptions&&typeof c.exceptions[day]==='boolean')return c.exceptions[day];return values(c.workdays).map(Number).includes(new Date(t).getUTCDay())&&!values(c.holidays).includes(day);}
 function businessOffset(state,id,t,n){var direction=n<0?-1:1,left=Math.abs(n),count=0;while(left&&count++<370){t+=direction*DAY;var work=workday(state,id,t);if(work==null)return null;if(work)left--;}return left?null:t;}
 function branchOkay(state,r,q){
  if(!['IDS-R012','IDS-R021','IDS-R019'].includes(r.id))return true;
  var b=confirmation(state,'branchConfirmations',r.id);return!!(b&&b.confirmedByMarine===true&&b.officeConfirmed===true&&b.caseId===state.caseId&&b.cycleId===state.cycleId&&b.branch===(q.stage||q.anchor)&&b.confirmationBasis&&Number.isFinite(Date.parse(b.confirmedAt)));
 }
 function applicable(state,r,q){
  if(['IDS-R002','IDS-R007','IDS-R035','IDS-R046'].includes(r.id)&&state.caseFactsConfirmed!==true)return false;
  if(r.id==='IDS-R002'&&!(state.tldScope==='pre_des'&&state.tldOfficeConfirmed===true))return false;
  if(q.anchor==='tdrl_certified_delivery_attempt'&&state.outcome!=='tdrl')return false;
  if(r.id==='IDS-R051'&&state.outcome!=='tdrl')return false;
  if(r.id==='IDS-R007'&&state.applicationTakenAway!==true)return false;
  if(r.id==='IDS-R044'&&!['pdrl','tdrl'].includes(state.outcome))return false;
  if(r.id==='IDS-R048'&&!['pdrl','tdrl'].includes(state.outcome))return false;
  if(r.id==='IDS-R046'&&state.coverageCategory!=='active_tamp')return false;
  if(r.id==='IDS-R035'&&!['hlr','board'].includes(state.vaReviewRoute))return false;
  if(r.id==='IDS-R035'&&(state.contestedClaim!==false||(q.anchor==='va_final_notice_issued'?'hlr':'board')!==state.vaReviewRoute))return false;
  if(q.anchor==='directed_hearing_notice_receipt'&&(state.hearingType!=='directed'||state.caseFactsConfirmed!==true))return false;
  return branchOkay(state,r,q);
 }
 function clock(state,rid,index,today,helpers){
  var r=byId[rid],q=r&&r.deadlines[index];if(!q||!state||state.schemaVersion!==1)return null;
  if(!applicable(state,r,q))return null;
  var mode=q.computation_status||'';
  if(mode==='SUPPRESS_COMPUTED_DEADLINE'||mode==='SUPPRESS_NOTICE_SUFFICIENCY_DETERMINATION')return null;
  var e=selected(state,rid,String(index),q.anchor,today);if(!e||!q.accepted_event_classifications.includes(e.classification))return null;
  var t=parse(e.date),adjust=q.weekend_holiday_adjustment?.rule,calId=q.business_calendar_id||q.weekend_holiday_adjustment?.business_calendar_id||q.weekend_holiday_adjustment?.holiday_calendar_id;
  if(q.calendar==='business_days'){t=businessOffset(state,calId,t,q.offset);}
  else if(q.unit==='years')t=months(t,q.offset*12);
  else if(q.unit==='months')t=months(t,q.offset);
  else if(q.unit==='days')t+=q.offset*DAY;
  if(t==null)return null;
  if(adjust==='next_business_day_if_day_15_nonbusiness'){
   for(var n=0;n<370;n++,t+=DAY){var w=workday(state,calId,t);if(w==null)return null;if(w)break;}if(n===370)return null;
  }else if(adjust==='next_succeeding_workday_if_saturday_sunday_holiday'||adjust==='next_succeeding_workday_if_saturday_sunday_legal_holiday'){
   // Shared Part 3 helper is supplied by the SML lane. No second rollover here.
   if(!helpers||typeof helpers.actualServiceEndOffset!=='function')return null;
   var offsetRule={months:q.unit==='years'?q.offset*12:q.offset,roll:'nextWorkday'};
   t=r.id==='IDS-R034'?helpers.actualServiceEndOffset(parse(e.date),offsetRule):helpers.actualServiceEndOffset(parse(e.date),offsetRule,function(day){return workday(state,calId,day);});if(t==null)return null;
  }
  return{date:iso(t),actor:q.actor,measurement:q.measurement_type,exclusive:q.inclusivity==='before',illustration:mode==='ILLUSTRATION_ONLY_NOT_DOWNSTREAM_ANCHOR',risk:mode==='DISPLAY_RISK_ONLY_COUNSEL_CONFIRMATION_REQUIRED',minimum:mode==='DISPLAY_MINIMUM_ONLY_NO_AUTOMATIC_WAIVER',source:q.source_ids,event:e,rule:q,requirement:r.id,index:index};
 }
 function saveEvent(state,type,event,selections,today){
  var error=eventError(state,type,event,today);if(error)throw Error(error);
  var next=copy(state),prior=event.supersedesOccurrenceId;
  if(next.events[type]?.[event.occurrenceId])throw Error('Keep the saved occurrence. Make a correction as a new occurrence.');
  if(prior){var old=next.events[type]?.[prior];if(!old||old.status==='superseded')throw Error('Choose the current occurrence being corrected.');if(old.caseId!==event.caseId||old.selectedForBranch!==event.selectedForBranch)throw Error('Correct an occurrence in this case and review cycle.');old.status='superseded';Object.values(next.selectedEvents||{}).forEach(function(selection){Object.keys(selection).forEach(function(key){if(selection[key]?.[prior])selection[key][prior].status='superseded';});});}
  (next.events[type]||(next.events[type]={}))[event.occurrenceId]=copy(event);
  selections.forEach(function(s){var r=byId[s.requirement],q=r&&r.deadlines[s.key],valid=q?q.anchor===type:s.key==='event:'+type&&r.items.includes(events[type].item);if(!valid)throw Error('This event does not supply that clock.');var choices=(next.selectedEvents[s.requirement]||(next.selectedEvents[s.requirement]={}))[s.key]||{};Object.values(choices).forEach(function(x){x.status='superseded';});choices[event.occurrenceId]={occurrenceId:event.occurrenceId,status:'confirmed'};next.selectedEvents[s.requirement][s.key]=choices;});
  return next;
 }
 function milestone(state,item,today){var type={ 'ides-fpeb':'formal_hearing_date','ides-referral':'ides_referral','ides-ipeb-receipt':'ipeb_findings_receipt','sep-eas':'service_end_authorized','ret-day':'medical_retirement_effective_date','va-service-end':'service_end_actual','va-decision':'va_final_notice_received','ides-tdrl-start':'tdrl_placement','sep-orders':'orders_issued','ret-orders':'orders_issued','eas-orders':'orders_issued'}[item];if(!type)return null;for(var r of byItem[item]||[]){var e=selected(state,r.id,'event:'+type,type,today);if(e)return e;}return null;}
 function allClocks(state,item,today,helpers){var rows=[];(byItem[item]||[]).forEach(function(r){r.deadlines.forEach(function(q,i){rows.push({requirement:r,index:i,rule:q,result:clock(state,r.id,i,today,helpers)});});});return rows;}
 function visible(state,item){
  if(item.user===true)return true;if(!byItem[item.id])return false;
  if(state.outcome==='fit'&&!['ides-stage','ides-referral','ides-counsel','ides-wwr','ides-retention-help','ides-exception-help','va-sickcall','va-vso'].includes(item.id))return false;
  var retirement=['ret-day','ret-orders','ret-pay','ret-id','ret-sbp','fam-tricare-ret','ides-retired-pay-check','ides-concurrent-pay','ides-crsc'];
  if(retirement.includes(item.id)&&!['pdrl','tdrl'].includes(state.outcome))return false;
  if(['ides-severance','ides-recoupment','fam-tamp'].includes(item.id)&&state.outcome!=='severance')return false;
  if(['ides-tdrl-followup','ides-tdrl-start'].includes(item.id)&&state.outcome!=='tdrl'&&state.stage!=='tdrl')return false;
  return true;
 }
 return{data:data,byId:byId,byItem:byItem,initial:initial,eventError:eventError,selected:selected,selectedId:selectedId,values:values,calendar:calendar,workday:workday,clock:clock,saveEvent:saveEvent,milestone:milestone,allClocks:allClocks,visible:visible,parse:parse,iso:iso,months:months};
}
// Shared lossless transport. IDES validates its own schema after decoding.
async function loadText(payload){
 if(typeof DecompressionStream!=='function')throw Error('IDES_DATA_UNAVAILABLE');
 if(payload.encoding!=='gzip-base64')throw Error('IDES_DATA_UNAVAILABLE');
 var raw=atob(payload.data),bytes=Uint8Array.from(raw,function(c){return c.charCodeAt(0);});
 var stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
 var decoded=await new Response(stream).arrayBuffer();if(decoded.byteLength>1000000)throw Error('IDES_DATA_UNAVAILABLE');
 return new TextDecoder('utf-8',{fatal:true}).decode(decoded);
}
async function load(payload){
 var data=JSON.parse(await loadText(payload));
 if(data.schemaVersion!==1||data.requirements.length!==56||Object.keys(data.events).length!==42||data.conflicts.length!==35)throw Error('IDES_DATA_UNAVAILABLE');
 return data;
}
global.MusterOutIDES={create:create,load:load,loadText:loadText,grossEstimate:grossEstimate,federalWorkday:federalWorkday};
})(typeof window!=='undefined'?window:globalThis);
