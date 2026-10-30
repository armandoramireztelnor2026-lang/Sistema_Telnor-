with open('static/script.js', 'r', encoding='utf-8') as f:
    js = f.read()

bad = '''        }
    }
    } else if (rolActual === \'proveedores\''''

good = '''        }
    } else if (rolActual === \'proveedores\''''

if bad in js:
    js = js.replace(bad, good, 1)
    with open('static/script.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("Fixed extra brace in static/script.js")
else:
    print("Pattern not found!")

