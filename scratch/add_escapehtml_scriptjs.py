# -*- coding: utf-8 -*-
with open('static/script.js', 'r', encoding='utf-8') as f:
    c = f.read()

target = "window.cargarTiempoGarantiaJefatura = async function() {"
helper = """if (typeof window.escapeHtml !== 'function') {
    window.escapeHtml = function(text) {
        if (!text) return '';
        var d = document.createElement('div');
        d.innerText = text;
        return d.innerHTML;
    };
}

window.cargarTiempoGarantiaJefatura = async function() {"""

if target in c:
    c = c.replace(target, helper, 1)

with open('static/script.js', 'w', encoding='utf-8') as f:
    f.write(c)

print("escapeHtml helper added safely to script.js")

