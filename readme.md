## Notes

Is it worth having fields that update automatically?
Or should ALL saves just be explicit?
i.e. refactor all the immediate save widgets instead of the passive ones?


## Issues

If you clear a form field, and then REFRESH, the old form data is still shown.
e.g. If you clear a required text field, then reload, it still shows a blank
field, even though the database value hasn't changed.

If you clear a form field, and then RELOAD, the expected data is shown.

If you add a new rack, enter some data, and then refresh before the rack
is valid and can be saved, all the entered form field data is lost.

Could show a message before refresh, to explain difference in refresh vs reload
vs F5 versus Ctrl+F5? This would help with discarding new data for objects
without a PK.
