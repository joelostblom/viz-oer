# Keep activation in the same shell as the command that uses its environment.
activate-uvr = . .uvr/activate

.PHONY: preview book
preview:
	$(activate-uvr) && uv run quarto preview textbook  # Needs && to run in the same shell

book:
	$(activate-uvr) && uv run quarto render textbook  # Needs && to run in the same shell
