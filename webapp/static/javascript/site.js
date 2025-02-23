
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

//////////////////////////////////////////////////////////////////////////////
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


///////////////////////////////////////////////////////////////////////////

// Vista previa de imagen en el modulo de Captura de Foto
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

//////////////////////////////////////////////////////////////////////////

/////  CARGA LOS DATOS EN EL FORMULARIO OFFCANVAS EDITAR USUARIO
document.addEventListener('DOMContentLoaded', function() {
    const userRows = document.querySelectorAll('table tr');

    userRows.forEach(row => {
        row.addEventListener('click', function() {
            const userId = this.dataset.userId;
            const usuario = this.dataset.userUsuario;
            const nombre = this.dataset.userNombre;
            const apellido = this.dataset.userApellido;
            const rol = this.dataset.userRol;

            document.getElementById('edit_user_id').value = userId;
            document.getElementById('edit_usuario').value = usuario;
            document.getElementById('edit_nombre').value = nombre;
            document.getElementById('edit_apellido').value = apellido;
            document.getElementById('edit_rol').value = rol;

            const editForm = document.getElementById('editUserForm');
            editForm.action = `/editar_usuario/${userId}`;

        });
    });
});


// FUNCION DE GEOLOCALIZACION
////////////////////////////////////////////////////////////////////////////////////

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    } else {
        alert("Geolocalización no soportada por este navegador.");
    }
}

function showPosition(position) {
    document.getElementById("latitud").value = position.coords.latitude;
    document.getElementById("longitud").value = position.coords.longitude;
    // Aquí puedes enviar el formulario automáticamente si lo deseas
    // document.getElementById("editUserForm").submit();
}

function showError(error) {
    switch (error.code) {
        case error.PERMISSION_DENIED:
            alert("El usuario denegó la solicitud de geolocalización.");
            break;
        case error.POSITION_UNAVAILABLE:
            alert("Información de ubicación no disponible.");
            break;
        case error.TIMEOUT:
            alert("La solicitud de geolocalización ha expirado.");
            break;
        case error.UNKNOWN_ERROR:
            alert("Ha ocurrido un error desconocido.");
            break;
    }
}