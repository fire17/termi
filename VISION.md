# Termi — VISION (verbatim)

> Captured 2026-07-06 from fire17, verbatim per the SACRED rule. The original message
> contained this vision pasted twice, identically; preserved once. Enrichment lives in
> README.md — never edit the quote below.

---

VISION: Termi - Termi is you Terminal Friend
it includes abunch of aswesome things like, psst (tips and warnings), auto recovered commands (auto fixes typos), native ai in terminal, questions and actions if combined with any harness - herdr++ and all modern things for dev env (like helping a junior setup their terminal for the first time), scolds the user if running on windows ps and not in wsl (then explain to them or how and why its curtially imporant for serious developer and engineers to not use windows and use linux wsl instead, its not scary, help them set it up with a harness if available) - checks if zsh and all the things (good status final battle tested beautiful modern statusline, fishlike autosuggestions, zoxide with fuzzy results as native cd via bettercd (which is awesome), and other things you think i am missing please recommend, and ill remember more things and we will add them. we want to be able to also help migrate or cherry pick from either your backups or setups that were sent from other people (friends or online) as well as share you own, and people can choose how much (or all) to take from your setup. if this becomes good we can work more on comunity features, if we manange to add sso (google account etc) or oauth , and be able to sign users in, all of the config and management could be easily synced accross signed in devices, so you never have to setup your teminal from scratch , 1-Command and you instantly return to the terminal you love and used too - it should be easy for people to add anything they already have on their system to their Termi. we will add more interactions, features, userstories, interfaces, and interactable hooks events and triggers and other powerfull tools, and have it easy for anyone to reproduce programatically, almost like docker from the future that is tailored to dev-envs and terminal holystic end-to-end experience
comes with its own cli, cli tui, and agent skills
needs to be feature rich and completely awesome and valuable for anyone, newcomers to the terminal aswell as experts with decades of terminal experience and even for them it will feel like a level up

---

## Addendum — 2026-07-13, verbatim (fire17)

> one more idea for termi - is that it should for every terminal and shell, make sure that great keyboard and mouse support exists for those, for example doing option control and command keys to jump correctly between words lines etc, plus the backspace to delete entire words etc, also clicking with the mouse to move the typing cursor or caret there, and shift option left and right to select text like in a normal application - we can think of more of to enrich the experience and make sure that it works in our shells in any terminal

## Addendum 2 — 2026-07-13, verbatim (fire17) — jumpto (F17)

> note - we can create a new type of ux - where pressing both command+option+left/right can enter a special jumpto mode where what is typed afterwards will search either forward or back for that string (case not sensitive and fuzzy too) and will jump to the next (or prev if left was used) point where there are good matches (need to think of simple ways to navigate while in jumpto mode)
>
> also first before making the jumpto feature (experimental, can be toggled off if set to off) make sure that the shift key addition to select text also works with command (or ctrl for windows) to mark entire lines

## Addendum 3 — 2026-07-13, verbatim (fire17) — universal env support, installer, agent skill, control-everything TUI (phase 2 kickoff)

> lets make sure that we are supporting all shells (not just zsh) and all other terminals too - we can test and prove support for all now - but we need to make sure that the env checks and mechanisms to making this
>   work for any case are already in place and the structure is ready to accept and extend to support newer cases in the future - and also very importantly - matermire that we can support everything also in windows powershell
>   - we need to have a good install script that is crossplatform, and auto recognizes the available shells (ps and wsl for windows) and terminals - shows the tested verified coverage for all of those - display a simple
>   onliner message that would tell an agent to activate a skill to support the current case env for the user (agentic skill that comes with termi and detects and installs it as a globally available skill for claude code,
>   codex, or any other detected harness (hermess openclaw pi opencode etc) - also allow to easily extend the lists of harnesses shells OSs and terminal combinations in the future
>   basically termi should elevate the terminal experience no matter what platform or stack or env you are in - note we need to add custom tmux and herdr optimizations from termi out of the box - remember that for later
>   also through the termi cli tui itself we need to be able to see everything and control everything that comes with termi to either activate setup or deactivate any of the subparts features or option we have now or will make
>   in the future - should be the best cli the world has ever seen - if its not at that level then the goal is not complete
>
>   please use the /highest-bar skill FIRST BEFORE ANYTHING ELSE -  and once everything is completely finished and working - then we can run /save_and_ship for termi

---

> integrity footer (highest-bar Phase 0, updated 2026-07-13): sha256 of everything above the last separator = b63b124bb28ce0920df979a1ecc3fdbc039d56c8b5be0f592516eb440161c3de
