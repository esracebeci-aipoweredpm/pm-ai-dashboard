function showSection(id, el) {
  document.querySelectorAll('section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-chip').forEach(c => c.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  el.classList.add('active');
  window.scrollTo({top: 0, behavior: 'smooth'});
}
