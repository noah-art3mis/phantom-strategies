# Prophetic Strategies

Design read: an experimental philosophical oracle for curious readers, with a dreamlike spectral language and an iridescent, cinematic visual direction. The art direction combines monumental, Control-inspired typography with very sparse controls. Design variance 9, motion intensity 8, visual density 2. Native HTML/CSS and Three.js fit the bespoke art direction; there is no claimed official design system.

The original source supplies the product behavior and content: four strategies, temperature, question, generation, imagined reference, and creator links. The live Streamlit URL could not be inspected because it entered a redirect loop. The GitHub source was used as the functional reference.

The whole page stays near-black with white text controls. A large uppercase Prophetic Strategies title overlaps an oversized iridescent apparition. Rainbow interference belongs to the artwork; the animated title uses silvery mother-of-pearl with muted pink, lavender, and green. Manrope supplies the display and body type. Strategy choices are plain text with an underline and moving pearl shimmer on the selected voice; the question uses a single writing line, submission is a text action, and the temperature control is omitted. There are no cards, filled buttons, custom logo, or marketing sections. On mobile, the artwork fades before the form to preserve legibility.

Animation communicates the apparition's unstable presence and subtly intensifies while awaiting a response. Autonomous drift dominates; cursor-driven rotation is intentionally barely perceptible and exponentially damped before it affects the sculpture. It stops outside the viewport and in hidden tabs. Reduced motion renders a still scene; a visible control overrides the pause preference for the current page session. Static artwork is always present beneath the optional WebGL renderer.

## Generated artwork

The word “Strategies” in the product title carries a continuous pearlescent sweep using a repeating CSS background-position animation. Matching endpoint colors keep the loop seamless. The existing motion pause control freezes the sweep, and reduced-motion preferences show the static gradient. The effect stays within the letters and does not move or resize the text.

Tool: built-in image generation. Final asset: `web/public/spectral-veil.webp`.

Prompt: “Use case: stylized-concept. Asset: atmospheric background for Phantom Strategies, an experimental philosophical oracle website. Wide landscape 1536x1024. An uncanny dark void with a monumental translucent folded glass membrane emerging on the RIGHT HALF, an organic apparition like a smoke veil made of thin soap film, spectral rainbow interference in pale cyan, molten orange, pink and ultraviolet. Almost black charcoal background #08090b, left half almost entirely empty dark negative space for website typography. Photorealistic high-end experimental 3D render, subtle grain, dreamlike annihilation shimmer, delicate caustics, deep shadows, no planets, no stars, no neon cyberpunk city. No text, no letters, no logo, no watermark. Sculptural, restrained composition but mesmerizing rainbow material.”

The gradient text has paint padding with compensating margins: tightly tracked glyphs can extend outside their inline box, and the final S must retain its full painted outline.

The page opens directly on the title; the motion toggle lives in the footer. Enter submits a query, Shift+Enter inserts a line break, and IME composition keeps its native Enter handling.
