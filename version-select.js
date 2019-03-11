     window.addEventListener("DOMContentLoaded", function() {

  var CURRENT_VERSION = document.querySelector('#docs-version').dataset.version;
  var CURRENT_PATH = window.location.pathname.split("/");
  var ix_to_swap = Math.max(0, CURRENT_PATH.findIndex(x => x === CURRENT_VERSION));

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
    try{
        var versions = JSON.parse(this.responseText);
    
    
        var realVersion = versions.find(function(i) {
          return i === CURRENT_VERSION;
        });
    
        var select = makeSelect(versions.map(function(i) {
          return {text: i, value: i === "latest" ? "null" : i};
        }), realVersion === "latest" ? "null" : realVersion);
        select.addEventListener("change", function(event) {
          window.location.href = CURRENT_PATH.map((i, ix) => ix === ix_to_swap ? this.value : i).filter(i => i !== "null").join("/");
        });
    
        var container = document.createElement("div");
        container.id = "version-selector";
        container.appendChild(select);
    
        var title = document.querySelector(document.querySelector('#docs-version').dataset.anchor_div);
        var height = window.getComputedStyle(title).getPropertyValue("height");
        container.style.height = height;
    
        title.appendChild(container);
      } catch (err) {}
  };
    xhr.send();
});