# Testing

## Requirements

- pytest
- pytest-cov

## Run tests

From this directory or the root directory, run:

```shell
$ pytest
```

## Notes

The functional tests occasionally hang. We have tried to figure out why, but the only thing that seems to fix it is the order in which the tests are run.

In order to achieve that, the tests were renamed and prefixed with a 4 digit number. The numbers group the tests in categories.

- 0xxx client services
- 1xxx doctor/medical
- 2xxx physical therapist
- 3xxx trainer
- 4xxx staff
- 5xxx wearables
- 6xxx in house tools
- 9999 remote client test, placing this test last seems to fix hanging

Within each group, the tests are numbered by the 10s, e.g. xx10, xx20, etc. That leaves room for future expansion, so a test can be inserted without renaming all of them.
