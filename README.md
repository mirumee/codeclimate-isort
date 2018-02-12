# codeclimate-isort

A Code Climate engine to run `isort` on Python code.


### Usage

Enable the engine in your **.codeclimate.yml**

```yml
engines:
  isort:
    enabled: true
```

Or pass the engine explicitly to `codeclimate`:

```console
$ codeclimate analyze -e isort
```