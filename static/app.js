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

  var modal = document.getElementById("hiring-modal");
  if (!modal) return;

  var modalMeta = document.getElementById("hiring-modal-meta");
  var modalBody = document.getElementById("hiring-modal-body");
  var lastFocus = null;

  function openModal(company, role, notes) {
    lastFocus = document.activeElement;
    modalMeta.textContent = company + (role ? " — " + role : "");
    if (notes && String(notes).trim()) {
      modalBody.textContent = notes;
      modalBody.classList.remove("muted");
    } else {
      modalBody.textContent = "No hiring info pasted yet.";
      modalBody.classList.add("muted");
    }
    modal.hidden = false;
    document.body.classList.add("modal-open");
    var closeBtn = modal.querySelector(".modal-close");
    if (closeBtn) closeBtn.focus();
  }

  function closeModal() {
    if (modal.hidden) return;
    modal.hidden = true;
    document.body.classList.remove("modal-open");
    if (lastFocus && typeof lastFocus.focus === "function") {
      lastFocus.focus();
    }
  }

  document.querySelectorAll(".info-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var notes = "";
      var source = document.getElementById(btn.getAttribute("data-notes-id"));
      if (source) {
        try {
          notes = JSON.parse(source.textContent || '""');
        } catch (err) {
          notes = source.textContent || "";
        }
      }
      openModal(
        btn.getAttribute("data-company") || "",
        btn.getAttribute("data-role") || "",
        notes
      );
    });
  });

  modal.querySelectorAll("[data-modal-close]").forEach(function (el) {
    el.addEventListener("click", closeModal);
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      closeModal();
    }
  });
})();
