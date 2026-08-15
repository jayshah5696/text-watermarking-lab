# Stage 5 ten-pair Gemma implementation demonstration

Each prompt used the same seed for control and watermarked generation. The table uses the
generation key and all eligible token occurrences.

| Prompt | Condition | Copied tokens | G/T | z | p-value | z > 3 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `stage-02-continuity` | control | 12 | 3/11 | 0.1741 | 0.490447 | no |
| `stage-02-continuity` | watermarked | 27 | 11/26 | 2.0381 | 0.035523 | no |
| `notebook` | control | 17 | 4/16 | 0.0000 | 0.500000 | no |
| `notebook` | watermarked | 21 | 7/20 | 1.0328 | 0.253546 | no |
| `library` | control | 29 | 8/28 | 0.4364 | 0.442901 | no |
| `library` | watermarked | 23 | 9/22 | 1.7233 | 0.075493 | no |
| `garden` | control | 28 | 8/27 | 0.5556 | 0.410806 | no |
| `garden` | watermarked | 18 | 8/17 | 2.1004 | 0.030144 | no |
| `train` | control | 34 | 8/33 | -0.1005 | 0.503205 | no |
| `train` | watermarked | 31 | 9/30 | 0.6325 | 0.387595 | no |
| `kitchen` | control | 25 | 9/24 | 1.4142 | 0.139962 | no |
| `kitchen` | watermarked | 20 | 9/19 | 2.2517 | 0.019823 | no |
| `workshop` | control | 43 | 15/42 | 1.6036 | 0.097279 | no |
| `workshop` | watermarked | 32 | 10/31 | 0.9333 | 0.287187 | no |
| `storm` | control | 36 | 7/35 | -0.6831 | 0.628511 | no |
| `storm` | watermarked | 33 | 12/32 | 1.6330 | 0.091556 | no |
| `museum` | control | 27 | 7/26 | 0.2265 | 0.483940 | no |
| `museum` | watermarked | 27 | 7/26 | 0.2265 | 0.483940 | no |
| `observatory` | control | 23 | 5/22 | -0.2462 | 0.518924 | no |
| `observatory` | watermarked | 21 | 5/20 | 0.0000 | 0.500000 | no |

## Copied continuations

### stage-02-continuity

Prompt: Early one morning Jack went up the hill. At the top he

Control: saw the entire valley bathed in a soft, ethereal glow.

Watermarked: saw the entire valley bathed in the soft, ethereal glow of the rising sun, a breathtaking spectacle that made him pause in his ascent.

### notebook

Prompt: The student opened the notebook and wrote down each result because

Control: the process of careful recording was crucial for understanding the underlying patterns and making subsequent deductions.

Watermarked: the process of careful recording was crucial for understanding the underlying principles and avoiding costly errors in the subsequent calculations.

### library

Prompt: When the neighborhood library lost power, the staff

Control: quickly switched to backup generators, ensuring that patrons could still access books and use the computers for a few crucial hours until the main power was restored.

Watermarked: quickly switched to backup generators, ensuring that patrons could still access resources and that essential services remained operational throughout the outage.

### garden

Prompt: After three weeks without rain, the community garden finally

Control: bloomed with a vibrant tapestry of green, the thirsty soil finally drinking deeply and the rows of vegetables stretching towards the sun with renewed vigor.

Watermarked: burst into a vibrant green, the thirsty soil drinking in the precious moisture like a sponge.

### train

Prompt: As the last train pulled into the station, the conductor noticed

Control: As the last train pulled into the station, the conductor noticed the silence that followed the rush of commuters was unusually heavy, broken only by the distant hum of city life.

Watermarked: As the last train pulled into the station, the conductor noticed the unusual silence hanging over the usually bustling platform, a stillness that felt heavy with unspoken tension.

### kitchen

Prompt: The cook tasted the soup, reached for the small jar, and

Control: a wave of unexpected spice washed over him, prompting him to add a pinch of dried chili flakes before serving the first bowl.

Watermarked: a wave of unexpected sweetness washed over him, prompting him to add a pinch of finely ground cinnamon.

### workshop

Prompt: When the wooden clock stopped at noon, the apprentice

Control: When the wooden clock stopped at noon, the apprentice, startled by the sudden silence, dropped the tools he was holding and stared at the dusty, unmoving hands, a strange sense of stillness settling over the workshop.

Watermarked: ...felt a strange stillness settle over the workshop, the usual clatter of tools and murmured conversations replaced by an unnerving silence that seemed to stretch into infinity.

### storm

Prompt: The forecast warned of a storm, so the neighbors gathered

Control: The forecast warned of a storm, so the neighbors gathered, their voices hushed with a shared sense of apprehension as the first heavy drops began to lash against the windowpanes.

Watermarked: The forecast warned of a storm, so the neighbors gathered, their voices hushed with a shared sense of apprehension as they debated the best way to secure their properties.

### museum

Prompt: Behind the newly restored painting, the curator discovered

Control: Behind the newly restored painting, the curator discovered a hidden compartment containing a series of faded letters and a small, tarnished locket.

Watermarked: Behind the newly restored painting, the curator discovered a hidden compartment containing a series of faded letters and a small, tarnished locket.

### observatory

Prompt: Just before dawn, the observatory computer recorded a signal that

Control: ...defied all known astrophysical models, a complex, rhythmic pattern emanating from a seemingly empty sector of deep space.

Watermarked: ...defied all known astrophysical models, a complex, repeating pattern emanating from a source impossibly distant.

## Interpretation

Probability under the configured no-watermark baseline of evidence at least this extreme; not the probability that the text is watermarked.

Ten paired prompts demonstrate the implementation and do not estimate detector accuracy, a false-alarm rate, quality preservation, or a production threshold.
