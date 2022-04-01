# \_FLObject

FLObject is the core of PyFLP's object model. It handles parsing of events
dispatched by `Parser` and saving them back by calling `dump` methods of
`Event`. `Parser` will use the `EventID` class inside a `_FLObject` to
instantiate it based upon the event ID.

::: pyflp._flobject._FLObject

::: pyflp._flobject._MaxInstancedFLObject
