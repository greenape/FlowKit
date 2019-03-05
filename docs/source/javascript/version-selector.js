     window.addEventListener("DOMContentLoaded", function() {
  function normalizePath(path) {
    var normalized = [];
    path.split("/").forEach(function(bit, i) {
      if (bit === "." || (bit === "" && i !== 0)) {
        return;
      } else if (bit === "..") {
        if (normalized.length === 1 && normalized[0] === "") {
          // We must be trying to .. past the root!
          throw new Error("invalid path");
        } else if (normalized.length === 0 ||
                   normalized[normalized.length - 1] === "..") {
          normalized.push("..");
        } else {
          normalized.pop();
        }
      } else {
        normalized.push(bit);
      }
    });
    return normalized.join("/");
  }

  // `base_url` comes from the base.html template for this theme.
  var REL_BASE_URL = ".";
  var ABS_BASE_URL = normalizePath(window.location.pathname + "/" +
                                   REL_BASE_URL);
  var CURRENT_VERSION = ABS_BASE_URL.split("/").pop();

  function makeSelect(options, selected) {
    var select = document.createElement("select");
    select.classList.add("form-control");

    options.forEach(function(i) {
      var option = new Option(i.text, i.value, undefined,
                              i.value === selected);
      select.add(option);
    });

    return select;
  }

  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/versions.json");
  xhr.onload = function() {
    var versions = JSON.parse(this.responseText);


    var realVersion = versions.find(function(i) {
      return i === CURRENT_VERSION;
    });

    var select = makeSelect(versions.map(function(i) {
      return {text: i, value: i};
    }), realVersion);
    select.addEventListener("change", function(event) {
      window.location.href = REL_BASE_URL + "/../" + this.value;
    });

    var container = document.createElement("div");
    container.id = "version-selector";
    container.appendChild(select);

    var title = document.querySelector("div.md-footer-meta__inner");
    var height = window.getComputedStyle(title).getPropertyValue("height");
    container.style.height = height;
    container.classList.add("md-footer-copyright")

    title.appendChild(container);
  };
  xhr.send();
});