import { EMAIL_STYLES, emailButton } from "./email_html.ts";
// Reader: a Marine who requested the guide. Effect: set up a Claude Project and coach.
// Keep the reviewed copy in paragraphs; private footer URLs are generated per send.
export const COACH_GUIDE_COPY = {
  "subject": "Your Muster Out coach setup guide",
  "preheader": "Create your Claude Project, add the coach instructions, and start your plan.",
  "heading": "Set up your Muster Out coach",
  "paragraphs": [
    "Your Muster Out coach keeps and reads the documents you add. It can check Gmail and your calendar after you connect them and approve access. It remembers your plan and the facts you approve for your board. A Claude Project keeps this work together so you can return to it. If you are helping a Marine, have them set this up in their own Claude account.",
    "1. In your own Claude account, open https://claude.ai/projects. Create a Project and name it Muster Out. If your phone app has no creation button, use the browser.",
    "2. Open https://musterout.warfarecommand.com/coach/ and tap Copy coach instructions. Paste the entire block into Project instructions and save. Copy the instructions from the guide so you get the current version.",
    "3. Start a chat inside that Project and send Start. Follow the guide; it walks you through the rest.",
    "Before uploading records, turn off Help improve Claude in Settings, then Privacy. Use web settings if the phone labels differ. Add your own records as they are to your private Project. The coach keeps identifiers out of board entries, notes and drafts for others. Ask the coach to cite the filename and page when it answers from a record.",
    "Connect Gmail and Google Calendar when you choose. Review the permissions in Claude. Approve any proposed send or calendar change separately. Use a computer if the phone path is missing.",
    "Return to this Project for your next question or say Check in. Your board holds the current plan; ask the coach to read it at each chat. Saving a fact or check-in to your board needs your separate approval."
  ],
  "reason": "You requested the coach setup guide and confirmed this address. This is one guide, with no setup follow-up emails. No open or click tracking.",
  "footer": "Warfare Command. Marine-built technology. Unofficial; not affiliated with the Department of Defense or the Marine Corps."
} as const;
const e = (s: string) => s.replace(/[&<>"']/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[c]!));
export function renderCoachGuide(links: { unsubscribeUrl: string; prefsUrl: string }, confirmation?: string) {
  const c = confirmation ? { ...COACH_GUIDE_COPY, subject: "Confirm your Muster Out coach guide request", heading: "Confirm your coach guide request", preheader: "Confirm your address to receive one coach setup guide.", paragraphs: ["You asked for the Muster Out coach setup guide. Confirm your address and we will email you the steps to set up your Claude Project and coach.", "This is one guide. It does not subscribe you to setup follow-ups, corrections, Monthly, weekly email, or lessons.", "If you did not request this guide, ignore this email. Your address will not be confirmed."], reason: "This address was entered on the Muster Out coach guide page." } : COACH_GUIDE_COPY;
  const guide = confirmation || "https://musterout.warfarecommand.com/coach/";
  const buttonLabel = confirmation ? "Confirm my email" : "Open the coach guide";
  const linked = (s: string) => e(s).replaceAll(guide, `<a href="${guide}" style="text-decoration:underline;overflow-wrap:anywhere;">${guide}</a>`).replaceAll('https://claude.ai/projects', '<a href="https://claude.ai/projects" style="text-decoration:underline;">claude.ai/projects</a>');
  // All head CSS uses literal values; primary actions also survive head removal.
  const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light dark"><meta name="supported-color-schemes" content="light dark"><title>${e(c.subject)}</title><style>
${EMAIL_STYLES}
</style></head><body style="margin:0;font-family:'IBM Plex Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;">
<div style="display:none;max-height:0;overflow:hidden;">${e(c.preheader)}</div>
<table role="presentation" class="email" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#F4F3EF"><tr><td align="center"><table role="presentation" class="wrap" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:720px;"><tr><td class="content" style="padding:16px;">
<div class="brand" style="border-bottom:2px solid #C8102E;padding-bottom:12px;"><img src="https://musterout.warfarecommand.com/assets/brand/email-header-600@2x.png" width="300" alt="Warfare Command" style="display:block;width:300px;max-width:100%;height:auto;background:#F4F3EF;color:#1C1C1E;"></div>
<h1 style="font-size:24px;line-height:1.25;margin:24px 0 12px;">${e(c.heading)}</h1>
<p style="font-size:16px;line-height:1.5;margin:0 0 16px;">${linked(c.paragraphs[0])}</p>
${emailButton(buttonLabel, guide)}
${c.paragraphs.slice(1).map(s => `<p style="font-size:16px;line-height:1.5;margin:0 0 16px;">${linked(s)}</p>`).join('\n')}
${!confirmation ? `<p style="font-size:16px;line-height:1.5;margin:0 0 24px;"><a href="${guide}">Open the coach guide</a></p>` : ""}
<div class="footer" style="border-top:1px solid #858580;padding-top:16px;">
<p class="email-muted" style="font-size:14px;line-height:1.5;margin:0 0 16px;">${e(c.reason)}</p>
<a href="${e(links.prefsUrl)}" style="display:block;min-height:48px;box-sizing:border-box;padding:12px 0;">Email preferences</a>
<a href="${e(links.unsubscribeUrl)}" style="display:block;min-height:48px;box-sizing:border-box;padding:12px 0;">Unsubscribe from everything</a>
<p class="email-muted" style="font-size:14px;line-height:1.5;margin:16px 0 0;">${e(c.footer)}</p>
</div></td></tr></table></td></tr></table></body></html>`;
  const text = [c.heading, ...c.paragraphs, `${buttonLabel}: ${guide}`, c.reason, `Email preferences: ${links.prefsUrl}`, `Unsubscribe from everything: ${links.unsubscribeUrl}`, c.footer].join("\n\n");
  return {html, text};
}

export const renderGuideConfirmation = (confirmUrl: string, unsubscribeUrl: string, prefsUrl: string) => renderCoachGuide({unsubscribeUrl, prefsUrl}, confirmUrl);
