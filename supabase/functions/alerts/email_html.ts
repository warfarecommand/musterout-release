// Email clients cannot rely on CSS custom properties. These literal values are
// the WC palette and scale; inline button styles must survive a stripped head.
export const EMAIL_STYLES = `
@font-face {font-family:'IBM Plex Sans';font-display:swap;src:url(https://musterout.warfarecommand.com/assets/fonts/ibm-plex-sans-latin.woff2) format('woff2');}
@font-face {font-family:'IBM Plex Sans Condensed';font-weight:600;font-display:swap;src:url(https://musterout.warfarecommand.com/assets/fonts/ibm-plex-sans-condensed-600-latin.woff2) format('woff2');}
body {margin:0;padding:0;font-family:'IBM Plex Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;}
.email {background-color:#F4F3EF;color:#1C1C1E;}
.email-panel {background-color:#FFFFFF;}
.email h1,.email p {color:inherit;overflow-wrap:anywhere;}
.email a {color:#A30D25;overflow-wrap:anywhere;}
.email .email-muted {color:#48484D;}
.email .email-button {color:#FFFFFF;background-color:#C8102E;}
@media (prefers-color-scheme:dark) {
  .email {background-color:#0B0B0C;color:#F5F5F7;}
  .email-panel {background-color:#161618;}
  .email a {color:#FF7B90;}
  .email .email-muted {color:#C2C2C7;}
  .email .email-button {color:#FFFFFF;background-color:#C8102E;}
}`;

const escape = (s: string) => s.replace(/[&<>"']/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[c]!));

export function emailButton(label: string, url: string): string {
  return `<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:0 0 24px;"><tr><td bgcolor="#C8102E" style="background-color:#C8102E;border-radius:8px;"><a class="email-button" href="${escape(url)}" style="display:inline-block;box-sizing:border-box;min-width:48px;min-height:48px;padding:12px 16px;border:1px solid #C8102E;border-radius:8px;background-color:#C8102E;color:#FFFFFF;font-family:'IBM Plex Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;font-size:16px;line-height:1.5;font-weight:600;text-decoration:none;text-align:center;">${escape(label)}</a></td></tr></table>`;
}
