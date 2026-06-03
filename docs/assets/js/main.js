(function () {
  // Highlight active nav/sidebar based on current page
  const page = location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll("nav a, .sidebar a").forEach(function (a) {
    var href = a.getAttribute("href");
    if (href === page || (page === "" && href === "index.html")) {
      a.classList.add("active");
    }
  });
})();
