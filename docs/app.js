(function () {
  var STORAGE_KEY = "applylog.applications";
  var STATUSES = ["applied", "interview", "offer", "rejected"];
  var DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/;
  var WIKI_SUMMARY =
    "https://en.wikipedia.org/api/rest_v1/page/summary/";

  var addForm = document.getElementById("add-form");
  var editForm = document.getElementById("edit-form");
  var editCard = document.getElementById("edit-card");
  var listEl = document.getElementById("list");
  var bannerEl = document.getElementById("banner");
  var editingId = null;

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function showBanner(message, kind) {
    bannerEl.hidden = false;
    bannerEl.textContent = message;
    bannerEl.className = "banner " + (kind || "success");
  }

  function loadApps() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      var parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed : [];
    } catch (err) {
      return [];
    }
  }

  function saveApps(apps) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(apps));
  }

  function nextId(apps) {
    var max = 0;
    for (var i = 0; i < apps.length; i++) {
      if (apps[i].id > max) max = apps[i].id;
    }
    return max + 1;
  }

  function sortNewestFirst(apps) {
    return apps.slice().sort(function (a, b) {
      if (a.date_applied !== b.date_applied) {
        return a.date_applied < b.date_applied ? 1 : -1;
      }
      return b.id - a.id;
    });
  }

  function placeTooltip(wrap) {
    var bubble = wrap.querySelector(".company-tip-bubble");
    if (!bubble) return;
    var trigger = wrap.getBoundingClientRect();
    var width = bubble.offsetWidth;
    var height = bubble.offsetHeight;
    var top = trigger.bottom + 8;
    if (top + height > window.innerHeight - 8) {
      var above = trigger.top - 8 - height;
      top = above >= 8 ? above : Math.max(8, window.innerHeight - 8 - height);
    }
    var left = trigger.left;
    if (left + width > window.innerWidth - 8) {
      left = window.innerWidth - 8 - width;
    }
    left = Math.max(8, left);
    bubble.classList.add("is-placed");
    bubble.style.top = top + "px";
    bubble.style.left = left + "px";
  }

  function bindTooltips() {
    listEl.querySelectorAll(".company-tip").forEach(function (wrap) {
      wrap.addEventListener("mouseenter", function () {
        placeTooltip(wrap);
      });
      wrap.addEventListener("focus", function () {
        placeTooltip(wrap);
      });
    });
  }

  function companyCell(app) {
    var name = escapeHtml(app.company);
    var info = (app.company_info || "").trim();
    if (!info) return name;
    return (
      '<span class="company-tip" tabindex="0">' +
      name +
      '<span class="company-tip-bubble" role="tooltip">' +
      escapeHtml(info) +
      "</span></span>"
    );
  }

  function renderList() {
    var apps = sortNewestFirst(loadApps());
    if (!apps.length) {
      listEl.innerHTML = '<p class="empty">No applications yet.</p>';
      return;
    }
    var rows = apps
      .map(function (app) {
        return (
          "<tr>" +
          "<td>" +
          companyCell(app) +
          "</td>" +
          "<td>" +
          escapeHtml(app.role) +
          "</td>" +
          "<td>" +
          escapeHtml(app.date_applied) +
          "</td>" +
          '<td><span class="status status-' +
          escapeHtml(app.status) +
          '">' +
          escapeHtml(app.status) +
          "</span></td>" +
          "<td>" +
          escapeHtml(app.notes || "") +
          "</td>" +
          '<td class="actions">' +
          '<button type="button" class="link-btn" data-edit="' +
          app.id +
          '">Edit</button>' +
          '<button type="button" class="danger" data-delete="' +
          app.id +
          '">Delete</button>' +
          "</td>" +
          "</tr>"
        );
      })
      .join("");
    listEl.innerHTML =
      '<div class="table-wrap"><table><thead><tr>' +
      "<th>Company</th><th>Role</th><th>Date applied</th>" +
      "<th>Status</th><th>Notes</th><th>Actions</th>" +
      "</tr></thead><tbody>" +
      rows +
      "</tbody></table></div>";
    bindTooltips();
  }

  function closeEdit() {
    editingId = null;
    editCard.hidden = true;
    editForm.reset();
  }

  function openEdit(app) {
    editingId = app.id;
    editCard.hidden = false;
    editForm.elements.id.value = String(app.id);
    document.getElementById("edit-company").textContent = app.company;
    document.getElementById("edit-role").textContent = app.role;
    document.getElementById("edit-date").textContent = app.date_applied;
    editForm.elements.status.value = app.status;
    editForm.elements.notes.value = app.notes || "";
    editCard.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function truncateSummary(text) {
    text = String(text || "").replace(/\s+/g, " ").trim();
    if (text.length <= 700) return text;
    var cut = text.slice(0, 700);
    var space = cut.lastIndexOf(" ");
    if (space >= 490) cut = cut.slice(0, space);
    return cut.replace(/[,;:\-\s]+$/, "") + "…";
  }

  function fetchCompanyInfo(company) {
    var url = WIKI_SUMMARY + encodeURIComponent(company);
    var timer = null;
    var controller = typeof AbortController !== "undefined" ? new AbortController() : null;
    if (controller) {
      timer = setTimeout(function () {
        controller.abort();
      }, 5000);
    }
    return fetch(url, {
      headers: { Accept: "application/json" },
      signal: controller ? controller.signal : undefined,
    })
      .then(function (res) {
        if (!res.ok) return "";
        return res.json();
      })
      .then(function (data) {
        if (!data || !data.extract) return "";
        return truncateSummary(data.extract);
      })
      .catch(function () {
        return "";
      })
      .finally(function () {
        clearTimeout(timer);
      });
  }

  addForm.addEventListener("submit", function (event) {
    event.preventDefault();
    var company = addForm.elements.company.value.trim();
    var role = addForm.elements.role.value.trim();
    var dateApplied = addForm.elements.date_applied.value.trim();
    var status = addForm.elements.status.value.trim();
    var notes = addForm.elements.notes.value.trim();
    if (!company || !role || !dateApplied) {
      showBanner("Company, role, and date applied are required.", "error");
      return;
    }
    if (!DATE_PATTERN.test(dateApplied)) {
      showBanner("Date applied must be YYYY-MM-DD.", "error");
      return;
    }
    if (STATUSES.indexOf(status) === -1) {
      showBanner("Status must be applied, interview, offer, or rejected.", "error");
      return;
    }
    var apps = loadApps();
    var row = {
      id: nextId(apps),
      company: company,
      role: role,
      date_applied: dateApplied,
      status: status,
      notes: notes,
      company_info: "",
    };
    apps.push(row);
    saveApps(apps);
    addForm.reset();
    addForm.elements.status.value = "applied";
    renderList();
    showBanner("Application saved.", "success");
    fetchCompanyInfo(company).then(function (info) {
      if (!info) return;
      var latest = loadApps();
      for (var i = 0; i < latest.length; i++) {
        if (latest[i].id === row.id) {
          latest[i].company_info = info;
          saveApps(latest);
          renderList();
          break;
        }
      }
    });
  });

  editForm.addEventListener("submit", function (event) {
    event.preventDefault();
    var id = Number(editForm.elements.id.value);
    var status = editForm.elements.status.value.trim();
    var notes = editForm.elements.notes.value.trim();
    if (STATUSES.indexOf(status) === -1) {
      showBanner("Status must be applied, interview, offer, or rejected.", "error");
      return;
    }
    var apps = loadApps();
    var found = false;
    for (var i = 0; i < apps.length; i++) {
      if (apps[i].id === id) {
        apps[i].status = status;
        apps[i].notes = notes;
        found = true;
        break;
      }
    }
    if (!found) {
      showBanner("Application not found.", "error");
      closeEdit();
      renderList();
      return;
    }
    saveApps(apps);
    closeEdit();
    renderList();
    showBanner("Application updated.", "success");
  });

  document.getElementById("edit-cancel").addEventListener("click", function () {
    closeEdit();
  });

  listEl.addEventListener("click", function (event) {
    var editBtn = event.target.closest("[data-edit]");
    var deleteBtn = event.target.closest("[data-delete]");
    if (editBtn) {
      var editId = Number(editBtn.getAttribute("data-edit"));
      var apps = loadApps();
      for (var i = 0; i < apps.length; i++) {
        if (apps[i].id === editId) {
          openEdit(apps[i]);
          return;
        }
      }
    }
    if (deleteBtn) {
      var deleteId = Number(deleteBtn.getAttribute("data-delete"));
      if (!window.confirm("Delete this application?")) return;
      var remaining = loadApps().filter(function (app) {
        return app.id !== deleteId;
      });
      saveApps(remaining);
      if (editingId === deleteId) closeEdit();
      renderList();
      showBanner("Application deleted.", "success");
    }
  });

  renderList();
})();
