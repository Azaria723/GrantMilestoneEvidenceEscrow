# Netlify production verification — 2026-09-02

Production URL: https://grantmilestoneevidenceescrow.netlify.app/

Netlify project ID: `64bab91e-03cd-4cb6-acdb-e2392f21e8e2`

Production deploy ID: `6a97ffbd3d3a7744b7646a45`

The deploy was uploaded from the locally verified `frontend/dist` build using the Netlify API account `azaria723`. The API reported `sso_login=false`, `account_sso_login=false`, and `has_password=false` for the site.

Executed public-browser checks:

- The HTTPS production URL loaded without authentication or a 404.
- The page displayed contract `0x37Eb0776f03fa1C18ac9F0F327335dfE9388b420` on Studionet 61999.
- After RPC readback, it displayed one grant and one milestone.
- Accounting displayed 0.001 GEN deposited, 0.001 GEN released, 0 GEN locked and 0 GEN refunded.
- Grant 0 displayed submission 3 and terminal `PAID` state.
- No browser console errors were observed.

Wallet signing was tested through the SDK lifecycle recorded in `studionet-e2e.md`, not by transmitting private keys through the browser. This deployment is currently an API/CLI production deploy. Automatic Git-triggered rebuilds were not claimed or tested.
