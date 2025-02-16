// JavaScript para cambiar la visibilidad de la contraseña
document.getElementById('show-password').addEventListener('change', function () {
    const passwordField = document.getElementById('password-field');
    if (this.checked) {
        passwordField.type = 'text';
    } else {
        passwordField.type = 'password';
    }
});

// Al hacer clic en el enlace, enviar el formulario
document.getElementById('submit-btn').addEventListener('click', function(e) {
    e.preventDefault();  // Prevenir que se haga la acción por defecto del enlace (navegar)
    
    // Enviar el formulario
    document.getElementById('login-form').submit();
});


 // Captura de la geolocalización
 function obtenerUbicacion() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {
            document.getElementById("ubicacion").value = position.coords.latitude + ", " + position.coords.longitude;
        });
    } else {
        alert("Geolocalización no soportada por este navegador.");
    }
}
window.onload = obtenerUbicacion;

// Vista previa de imagen
function previewImage(event) {
    const input = event.target;
    const preview = document.getElementById("preview");

    if (input.files && input.files[0]) {
        const reader = new FileReader();

        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = "block";
        };

        reader.readAsDataURL(input.files[0]);
    }
}