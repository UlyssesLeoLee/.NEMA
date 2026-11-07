# Ariadne 3D home hero — implementation and art direction

## Artistic contract

- Classical **Greek marble statue**, not skin-shaded anime / realistic actress.
- American comic linework: meaningful thick dark contour silhouettes and crisp discrete toon shadow masses.
- Supporting scene should be quieter than the character: thin gold outline halo, no noisy particles or unnecessary bloom.
- **Golden yarn ball in the statue's raised hand** as the main motif, with a flowing line that maps to NEMA's graph-and-thread semantics.
- Original R7 website palette and geometry retained. Only homepage hero composition is enhanced.

## Runtime

`website/three-hero.js` builds the bust, face, laurel, drapery, supporting hand, yarn ball, connected gold thread, and a minimal plinth using Three.js primitives and TubeGeometry. Animations include modest bust yaw, yarn turn, and a repeating signal along the thread; they do not hide other parts of the scene.

Rendering pauses when the hero leaves the viewport or the page is hidden. Resizes follow ResizeObserver. WebGL resources are disposed on pagehide. If the user requests reduced motion, the original static image is displayed instead. If CDN/module/WebGL fails, the same static image serves as a fallback.

## QA limitations

This is a procedural stylized sculpture built for the hero section; full sculptural anatomy is intentionally simplified. Detailed browser-level visual validation with network-enabled CDN should be performed after deployment, since local offline environments render the fallback image.
