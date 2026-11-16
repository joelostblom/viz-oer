# Keep activation in the same shell as the command that uses its environment.
activate-uvr = . .uvr/activate

.PHONY: preview book slides
preview:
	$(activate-uvr) && uv run quarto preview  # Needs && to run in the same shell

book:
	$(activate-uvr) && uv run quarto render  # Needs && to run in the same shell

# Book/preview renders already build slides through Quarto's post-render hook.
slides:
	$(activate-uvr) && uv run python src/build_chapter_slides.py --force
