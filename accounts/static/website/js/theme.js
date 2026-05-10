(function () {
  const root = document.documentElement;
  const saved = localStorage.getItem('mk-theme');
  if (saved === 'dark') root.classList.add('dark');
  if (saved === 'light') root.classList.remove('dark');

  document.querySelectorAll('[data-theme-toggle]').forEach(function (button) {
    button.addEventListener('click', function () {
      root.classList.toggle('dark');
      localStorage.setItem('mk-theme', root.classList.contains('dark') ? 'dark' : 'light');
    });
  });
})();
