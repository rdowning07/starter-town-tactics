# Walk/Attack + FX Pack

Adds walk/attack for Knight & Goblin and FX (spark, slash). Demo scenario included.

## Files
- assets/units/knight/{idle,walk,attack}.png
- assets/units/goblin/{idle,walk,attack}.png
- assets/units/_metadata/animation_metadata.json
- assets/effects/spark/sheet.png
- assets/effects/slash/sheet.png
- assets/effects/_metadata/effects_metadata.json
- devtools/scenarios/units_fx_demo.yaml

## Keybind suggestions (wire in your input layer)
- SPACE → spawn 'spark' at knight
- A → play knight 'attack' once, then revert to 'idle'
- W → toggle goblin 'walk'

## Notes
- Respect coding standards: specific exceptions, encoding='utf-8', import order.
- Keep draw order: terrain → units → fx → ui.
