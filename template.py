HEADER = '''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.3.1/styles/atom-one-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.3.1/highlight.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlightjs-line-numbers.js/2.9.0/highlightjs-line-numbers.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.3.1/languages/java.min.js"></script>
    <script>hljs.highlightAll();hljs.initLineNumbersOnLoad({singleLine: true});</script>
    <style>
    body {
        background: #bcbcbc;
        padding: 0 24px;
        margin: 0;
        color: black;
        display: flex;
        justify-content: flex-start;
        flex-direction: column;
        align-items: flex-start;
    }
    table, th, td {
        border: 3px solid black;
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
        width: auto;
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
        text-align: left;
        font-size: 1.1em;
    }
    .hljs-ln-numbers {
        -webkit-touch-callout: none;
        -webkit-user-select: none;
        -khtml-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;

        text-align: center;
        color: #ccc;
        border-right: 1px solid #CCC;
        vertical-align: top;
        padding-right: 5px;

        /* your custom style here */
        width: 40px; /* Fixed width for line numbers */
        min-width: 40px; /* Ensure it doesn't shrink */
        box-sizing: border-box; /* Include padding in width */
    }
    /* for block of code */
    .hljs-ln-code {
        padding-left: 10px;
        border: 1px solid black;
    }
    .seperator {
        font-size: 1.2em;
    }
    .packagename {
        color: #d70087;
        font-size: 1.4em;
    }
    .filepath {
        font-size: 1.2em;
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
