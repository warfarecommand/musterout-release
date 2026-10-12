# Muster Out

Warfare Command publishes signed Muster Out board releases under the MIT license. A board verifies the release before offering Update now. Publishing requires Claude Pro and permission to update the board.

The owner signs board.publish.html offline with tools/release_sign.py. The release workflow verifies the signature against public_keys.json before publishing to npm with provenance. Configure [npm trusted publishing](https://docs.npmjs.com/trusted-publishers/) for the public release repository and npm-publish.yml. Keep the signing key offline with the owner throughout the release process.

The package skeleton contains no release.js until the signing ceremony. Public key maps are empty until the owner supplies production public roots. Verification fails with empty roots. Test keys belong in isolated temporary directories.

For setup and the pasted update path, read the [public release repository](https://github.com/warfarecommand/musterout-release).
