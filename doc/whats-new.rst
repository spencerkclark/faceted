.. _whats-new:

##########
What's New
##########

.. _whats-new.0.2:

v0.2 (unreleased)
=================

- :py:meth:`faceted.faceted` now supports three types of constrained figures:
  width-and-aspect constrained (as before), height-and-aspect constrained, and
  width-and-height constrained.  Note the you must provide exactly two of the
  ``width``, ``height``, and ``aspect`` arguments in your call.  A minor
  breaking change is that defaults are no longer provided for ``width`` and
  ``aspect`` (it would be cumbersome to have to override one of them with
  ``None`` in the case of creating a height-and-aspect constrained or
  width-and-height constrained figure).
- A new convenience function for creating single-axis figures called
  :py:meth:`faceted.faceted_ax`.  It takes the same keyword arguments as the
  full :py:meth:`faceted.faceted` function, except automatically returns
  scalar ``Axes`` objects.

.. _whats-new.0.1:

v0.1 (2019-03-07)
=================

- Initial release.  Note the name has changed since the development version from
  ``facets`` to ``faceted``.
- Default ``cbar_short_side_pad`` is now 0.0 instead of 0.5 inches.
