# Development

## Pre Requisites

- [Just]
- [Rust]
- [Near-cli]
- [Python]

## Getting Started

```bash

$ git clone https://github.com/Yonder-Labs/rebalancer.git

$ just setup-dev
```

## Compilation

Ensure the project compiles by running:

```bash
$ just build-contract # for a quick check

$ just build-with-docker # for testnet and production mode
```

## Commands

> just create-account <Account Name>

Example:

`just create one-thing.testnet`

## Scripts

<!-- REFERENCES -->
[Just]: https://github.com/casey/just
[Rust]: https://rust-lang.org/learn/get-started/
[Near-cli]: https://docs.near.org/tools/near-cli
[Python]: https://www.python.org/downloads/