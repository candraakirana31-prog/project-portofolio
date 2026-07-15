document.addEventListener('DOMContentLoaded', function () {
  // Konfirmasi sebelum menghapus data (proyek, pesan, skill)
  document.querySelectorAll('form[data-confirm]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      const message = form.getAttribute('data-confirm') || 'Yakin ingin menghapus data ini?';
      if (!window.confirm(message)) {
        e.preventDefault();
      }
    });
  });

  // Auto-hilangkan pesan flash setelah beberapa detik
  document.querySelectorAll('.flash').forEach(function (el, i) {
    setTimeout(function () {
      el.style.transition = 'opacity .4s ease';
      el.style.opacity = '0';
      setTimeout(function () { el.remove(); }, 400);
    }, 4000 + i * 300);
  });

  // Preview gambar sebelum upload
  document.querySelectorAll('input[type="file"][data-preview]').forEach(function (input) {
    input.addEventListener('change', function () {
      const targetId = input.getAttribute('data-preview');
      const target = document.getElementById(targetId);
      if (target && input.files && input.files[0]) {
        target.src = URL.createObjectURL(input.files[0]);
      }
    });
  });
});
