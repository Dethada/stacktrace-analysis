# Stack Trace Analysis Tool

## Requirements
- Python version >= 3.11
- poetry for package management

## Setup
```bash
poetry install
```

## Usage
```
usage: main.py [-h] projects_root input_file output_file

Find code lines from stack traces

positional arguments:
  projects_root  Path to the root directory of the projects
  input_file     Path to input file containing stack traces
  output_file    Path to output file for code lines

options:
  -h, --help     show this help message and exit
```

## Example
```
$ ls -la ~/projects
drwxr-xr-x    - david 16 Apr  2024 anima
drwxr-xr-x    - david  3 Mar  2024 asterisk-java
drwxr-xr-x    - david 23 Feb  2024 commons-configuration
drwxr-xr-x    - david  4 Oct  2023 commons-net
$ poetry run python3 ./main.py ~/projects ./input.toml ./output.html
```

Sample input and output files are available in the `example/` directory.

Sample `input.toml`
```toml
originating_test="io.lettuce.core.RedisClientFactoryUnitTests#clientResources"
algorithm="shb"
field_declaration="""
/**
 * Threading - synchronized(this). We are required to hold the monitor to use Java's underlying wait()/notifyAll().
 */
private short waiters;
"""
stack_trace="""
==================Stack Trace==================
io.netty.util.concurrent.DefaultPromise.checkNotifyWaiters(DefaultPromise.java:648))
io.netty.util.concurrent.DefaultPromise.setValue0(DefaultPromise.java:635))
io.netty.util.concurrent.DefaultPromise.setSuccess0(DefaultPromise.java:625))
	==================Stack Trace==================
	io.netty.util.concurrent.DefaultPromise.incWaiters(DefaultPromise.java:658))
	io.netty.util.concurrent.DefaultPromise.await0(DefaultPromise.java:697))
	io.netty.util.concurrent.DefaultPromise.await(DefaultPromise.java:295))
"""
```

