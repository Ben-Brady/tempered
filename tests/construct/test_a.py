from tempered import Tempered


def test_template_add_styles():
    components = Tempered()
    components.add_template("foo", """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset='utf-8'>
            <meta http-equiv='X-UA-Compatible' content='IE=edge'>
            <meta name='viewport' content='width=device-width, initial-scale=1'>
            <title>YourTube</title>
            <script src="https://unpkg.com/htmx.org@1.9.6"></script>
            {!styles!}
        </head>

        <style global>
            body {
                margin: 0;
                padding: 0;
                font-family: sans-serif;
                font-size: 12px;
                color: var(--text);
                background: var(--background);
            }

            body[data-theme="light"] {
                --text: #080708;
                --background: #f8f7f8;
                --primary: #7e7d72;
                --secondary: #e0dce0;
                --accent: #727e7d;
            }
            body[data-theme="dark"] {
                --text: #f8f7f8;
                --background: #080708;
                --primary: #8d8c81;
                --secondary: #231f23;
                --accent: #818d8c;
            }

            body {
            font-family: 'Didact Gothic';
            font-weight: 400;
            }

            h1, h2, h3, h4, h5 {
            font-family: 'Didact Gothic';
            font-weight: 700;
            }

            html {font-size: 100%;} /* 16px */

            h1 {font-size: 4.210rem; /* 67.36px */}

            h2 {font-size: 3.158rem; /* 50.56px */}

            h3 {font-size: 2.369rem; /* 37.92px */}

            h4 {font-size: 1.777rem; /* 28.48px */}

            h5 {font-size: 1.333rem; /* 21.28px */}

            small {font-size: 0.750rem; /* 12px */}
        </style>
        """)
    modules = components.build_memory()
    html = modules.foo()
    assert html

