// This file is intentionally blank
// Use this file to add JavaScript to your project

function dget(id){return document.getElementById(id)}

function is_empty(cmp){return dget(cmp).value.trim().length < 1}

function message(msg, type){
        $.toast({
            //heading: 'Error',
            text: msg,
            position: 'top-center',
            icon: type,
            stack: true
        })
}

function add_product(){
    //validando campos obligatorios
    if (is_empty('n_product')){
        message('Falta el nombre', 'error');
        dget('n_product').focus();
        return;
    }
    if (is_empty('d_product')){
        message('Falta la descripción', 'error');
        dget('d_product').focus();
        return;
    }
    if (is_empty('p_product')){
        message('Falta el precio', 'error');
        dget('p_product').focus();
        return;
    }
    if (is_empty('t_product')){
        message('Falta el contacto', 'error');
        dget('t_product').focus();
        return;
    }
    if (is_empty('file_1_b64')){
        message('Agregue  1 foto', 'error');
        return;
    }
    let csrftoken = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    jQuery.ajax({
        url: '/new_product/', type: 'POST', async: true,
        beforeSend: function (xhr, settings) {
            if (!this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        },
        data: {"pk_product": dget('pk_product').value, "n_product": dget('n_product').value,
            "d_product": dget('d_product').value,
            "p_product": dget('p_product').value, "t_product": dget('t_product').value,
            "file_1_b64": dget('file_1_b64').value },
        success: function(r) {
            dget('pk_product').value = "0";
            message('Producto guardado', 'success');
            dget('n_product').value = "";
            $("#d_product").summernote("reset");
            dget('p_product').value = "";
            dget('t_product').value = "";
            dget('img_1').src = "static/kernel/assets/addpic.png";
        },
        error: null
    });
}

function go_base(){
    window.location = '/';
}

function del_product(){
    jQuery.ajax({
        url: '/del_product/', type: 'GET', async: true,
        data: {"pk_product": dget('pk_product').value },
        success: function(r) {
            message('Producto eliminado', 'success');
        },
        error: null
    });
}

//para el menú contextual
(function (window, document) {

    function getElements() {
        return {
            layout: document.getElementById('layout'),
            menu: document.getElementById('menu'),
            menuLink: document.getElementById('menuLink')
        };
    }

    function toggleClass(element, className) {
        let classes = element.className.split(/\s+/);
        let length = classes.length;
        let i = 0;

        for (; i < length; i++) {
            if (classes[i] === className) {
                classes.splice(i, 1);
                break;
            }
        }
        // The className is not found
        if (length === classes.length) {
            classes.push(className);
        }

        element.className = classes.join(' ');
    }

    function toggleAll() {
        let active = 'active';
        let elements = getElements();

        toggleClass(elements.layout, active);
        toggleClass(elements.menu, active);
        toggleClass(elements.menuLink, active);
    }

    function handleEvent(e) {
        let elements = getElements();

        if (e.target.id === elements.menuLink.id) {
            toggleAll();
            e.preventDefault();
        } else if (elements.menu.className.indexOf('active') !== -1) {
            toggleAll();
        }
    }

    document.addEventListener('click', handleEvent);

}(this, this.document));
