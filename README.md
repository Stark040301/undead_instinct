# Undead Instinct

> Where the dead obey instincts and the world obeys equations.

**Undead Instinct** is a Python ecosystem simulator where creatures are programmed in
their own language, *Instinct*, and left to survive in a tick-based 2D world. It is
built as the Object-Oriented Programming course project, on a clean architectural
foundation that allows extending the same project later with a numerical analysis
layer (population ODEs, Euler/RK4 solvers, error and stability analysis).

Theme: **zombie apocalypse** — humans (susceptible), zombies (infected), survivors
(recovered), modeled after the SZR compartmental system.

---

## What it does

- **Instinct language**: creatures are programmed in `.ins` files with a header
  (creature, faction, health, vision, lifespan) and a body (`start:`, `goto`,
  `if expr goto`, assignments, actions).
- **Seven base actions**: `move`, `attack`, `consume`, `reproduce`, `roar`, `say`, `wait`.
- **Expressions**: integers, text, arithmetic, comparisons, `and/or/not`, `see(x,y)`,
  `name(x,y)`, constants and perceptions. Integers and text only — no floats.
- **World**: 2D grid of terrain (always) plus at most one object or one creature.
  Terrain regenerates; objects deplete; creatures age and die. Ticks advance the world.
- **UI**: load maps, place creatures, play/pause/step, adjust speed, read the log.
- **Headless**: the world runs from the terminal without the UI.
