# AI USAGE

## Where AI helped
- Gathering knowledge and creating practical examples to show implementation of
  different module that i used in the project.

## Prompts or strategies that worked
- Composition approach, i tried a "1-shot" strategy but that did not work so
well, issues with token's maxing out. Then i used a more of a composition
strategy to build out the project from my base models going up.

## Verification steps (tests, assertions, manual checks)
- The project is build to foundationally rely on type-safety, so that
eliminates a lot of tests and validation i have would otherwise have to do, as i
can use constraints and rely on pyrefly for type evaluation at "comptime".

## Cases where you chose **not** to use AI and why
- Project design (Architecture)
I found that it was easier to reason about the project, how it should work and
incorporate the features i want to add if, i don't rely on AI because part of
any addition i would make means i have to reason about the application state,
and if i don't design that myself it is very difficult to immediately know how a
new feature would interact with the whole application or what changes it would
cause.
