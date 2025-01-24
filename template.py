HEADER = '''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="src/style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/java.min.js"></script>
    <script>hljs.highlightAll();</script>
    <style>
    body {
        background: #f8f9fa;
        padding: 0 24px;
        margin: 0;
        color: black;
        display: flex;
        justify-content: flex-start;
        flex-direction: column;
        align-items: flex-start;
    }
    table, th, td {
        border: 1px solid black;
    }
    .header {
        width: 100%;
        text-align: center;
        margin: 0 auto;
    }
    .table-container {
        width: 80%;
        margin: 0 auto;
    }
    table {
        width: 100%;
        table-layout: fixed; /* Ensures equal column distribution */
        border-collapse: collapse;
    }
    th, td {
        width: 50%; /* Split columns equally */
        vertical-align: top;
        padding: 10px;
    }
    pre {
        margin: 0;
        white-space: pre-wrap; /* Preserve formatting but allow wrapping */
    }
    .wrap {
        overflow-wrap: break-word; /* Break long words */
        word-break: break-all; /* Ensure breaks happen if needed */
        white-space: pre-wrap;      /* Respect pre-formatted wrapping */
    }
    .large-code {
        font-size: 1.2em;
        overflow-wrap: break-word;  /* Break long words */
        word-break: break-all;      /* Ensure breaks happen if needed */
        white-space: pre-wrap;      /* Respect pre-formatted wrapping */
    }
    .header-code {
        width: 40%;
        overflow-x: auto;
        margin: 0 auto;
        padding-bottom: 15px;
    }
    </style>
  </head>
'''

TABLE_HEADER = '''
  <body>
    <div class="table-container">
    <table>
  <thead>
    <tr>
      <th><h2>Stack Trace 1</h2></th>
      <th><h2>Stack Trace 2</h2></th>
    </tr>
  </thead>
  <tbody>
'''

FOOTER = '''
  </tbody>
</table>
</div>

  </body>
</html>
'''
