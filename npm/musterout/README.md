# Muster Out

Warfare Command publishes Muster Out under the MIT license. Setup needs a chat that can run the security check and the normal publication permissions. Existing boards use their installed verifier for Update now.

Set up Muster Out for me. Check https://cdn.jsdelivr.net/npm/musterout@0.2.13/verify.cjs (SHA-256 88f05a85766ffae6618292535156f22fca31d811b8c3ae68307e736b89d6a40a) and https://cdn.jsdelivr.net/npm/musterout@0.2.13/verify.py (SHA-256 70cd6d5e61bfbabce4aeba8e3bbb5d7c6109db8993f2221684fdaf35fa07ee74), then follow the setup guide they verify.

The independently received setup message pins both dependency-free protocol-1 verifiers. The helper authenticates the publisher signature on install.json and release.js, all product files, and the exact board fragment/full document before any guide is followed. Transports are parsed as data, never executed. Release and feed roots are populated. Failed checks stop protected work and keep existing boards and recovery records.

The package contains release.js, signed install.json, the reviewed public install/ files, verify.cjs, verify.py, metadata and LICENSE. No scripts or installation hooks. Exact versions on jsDelivr and unpkg support confirmed-version recovery; availability is checked separately. The owner signs offline with tools/release_sign.py, then its --install branch. The proposed public workflow change must be applied by the supervisor before release. No private key reaches CI or a Marine.

Old copied instructions read from compromised main cannot be protected. Refresh them from the official Muster Out site. A page update does not refresh saved Project instructions or folder skills.
