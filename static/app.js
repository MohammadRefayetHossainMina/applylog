(function () {
  var GAP = 8;
  var PAD = 8;

  function place(wrap) {
    var bubble = wrap.querySelector(".company-tip-bubble");
    if (!bubble) return;
    var trigger = wrap.getBoundingClientRect();
    var width = bubble.offsetWidth;
    var height = bubble.offsetHeight;
    var top = trigger.bottom + GAP;
    if (top + height > window.innerHeight - PAD) {
      var above = trigger.top - GAP - height;
      if (above >= PAD) {
        top = above;
      } else {
        top = Math.max(PAD, window.innerHeight - PAD - height);
      }
    }
    var left = trigger.left;
    if (left + width > window.innerWidth - PAD) {
      left = window.innerWidth - PAD - width;
    }
    left = Math.max(PAD, left);
    bubble.classList.add("is-placed");
    bubble.style.top = top + "px";
    bubble.style.left = left + "px";
  }

  document.querySelectorAll(".company-tip").forEach(function (wrap) {
    wrap.addEventListener("mouseenter", function () {
      place(wrap);
    });
    wrap.addEventListener("focus", function () {
      place(wrap);
    });
  });
})();
