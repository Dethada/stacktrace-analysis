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
poetry run python3 ./main.py ~/<java project dir> input.toml output.html
```

## Example
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

