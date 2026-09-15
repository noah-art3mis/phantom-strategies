import "./styles.css";
import { consult } from "./consult.js";

const $ = (id) => document.getElementById(id);
const form = $("consult-form");
const submit = form.querySelector('button[type="submit"]');
const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");
let paused = reducedMotion.matches;
let scene;

function updateMotion() {
  document.body.classList.toggle("motion-paused", paused);
  $("motion-toggle").setAttribute("aria-pressed", String(paused));
  $("motion-toggle").textContent = paused
    ? "Resume motion ▷"
    : "Pause motion Ⅱ";
  scene?.setPaused(paused);
}
$("motion-toggle").addEventListener("click", () => {
  paused = !paused;
  updateMotion();
});
reducedMotion.addEventListener("change", (event) => {
  paused = event.matches;
  updateMotion();
});
updateMotion();

$("question").addEventListener("input", () => {
  $("question-count").value = $("question").value.length;
  $("question").setCustomValidity("");
});
$("temperature").addEventListener("input", () => {
  $("temperature-value").value = Number($("temperature").value).toFixed(1);
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = $("question").value.trim();
  if (!question) {
    $("question").setCustomValidity("Give the oracle a question to work with.");
    $("question").reportValidity();
    return;
  }
  const request = {
    question,
    strategy: new FormData(form).get("strategy"),
    temperature: Number($("temperature").value),
  };
  submit.disabled = true;
  $("voice-options").disabled = true;
  $("question").disabled = true;
  $("temperature").disabled = true;
  $("submit-label").textContent = "Listening...";
  $("form-error").hidden = true;
  $("response").hidden = false;
  $("response").setAttribute("aria-busy", "true");
  $("response-status").textContent = "A thought is taking shape...";
  $("loading-lines").hidden = false;
  $("answer").textContent = "";
  $("attribution").textContent = "";
  $("reference").textContent = "";
  $("fiction-note").hidden = true;
  scene?.setListening(true);
  try {
    const answer = await consult(request);
    $("answer").textContent = answer.content;
    $("attribution").textContent = `${answer.author}, the ${answer.strategy}`;
    $("reference").textContent = `${answer.book} · Sentence ${answer.sentence}`;
    $("fiction-note").hidden = false;
    $("response-status").textContent = "The oracle has spoken.";
    $("response").scrollIntoView({
      behavior: paused ? "instant" : "smooth",
      block: "nearest",
    });
  } catch (error) {
    $("response").hidden = true;
    $("form-error").hidden = false;
    $("form-error").textContent =
      error.name === "TimeoutError"
        ? "The oracle took too long to respond. Please try again."
        : error instanceof TypeError
          ? "The connection to the oracle was lost. Please try again."
          : error.message;
  } finally {
    submit.disabled = false;
    $("voice-options").disabled = false;
    $("question").disabled = false;
    $("temperature").disabled = false;
    $("submit-label").textContent = "O, Prophet...";
    $("loading-lines").hidden = true;
    $("response").setAttribute("aria-busy", "false");
    scene?.setListening(false);
  }
});

// Keep the form immediately usable while the decorative renderer downloads.
import("./scene.js")
  .then(({ createScene }) => {
    scene = createScene($("spectral-scene"), paused);
  })
  .catch(() => {
    // The locally hosted glass-veil artwork remains visible without WebGL.
  });
window.addEventListener("pagehide", () => scene?.dispose());
