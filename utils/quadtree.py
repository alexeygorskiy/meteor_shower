"""http://www.pygame.org/wiki/QuadTree"""
class QuadTree(object):
    """An implementation of a quad-tree.

    This QuadTree started life as a version of [1] but found a life of its own
    when I realised it wasn't doing what I needed. It is intended for static
    geometry, ie, items such as the landscape that don't move.

    This implementation inserts items at the current level if they overlap all
    4 sub-quadrants, otherwise it inserts them recursively into the one or two
    sub-quadrants that they overlap.

    Items being stored in the tree must possess the following attributes:

        left - the x coordinate of the left edge of the item's bounding box.
        top - the y coordinate of the top edge of the item's bounding box.
        right - the x coordinate of the right edge of the item's bounding box.
        bottom - the y coordinate of the bottom edge of the item's bounding box.

        where left &lt; right and top &lt; bottom

    ...and they must be hashable.

    Acknowledgements:
    [1] http://mu.arete.cc/pcr/syntax/quadtree/1/quadtree.py
    """

    def __init__(self, items, depth=8, bounding_rect=None):
        """Creates a quad-tree.

        @param items:
            A sequence of items to store in the quad-tree. Note that these
            items must possess left, top, right and bottom attributes.

        @param depth:
            The maximum recursion depth.

        @param bounding_rect:
            The bounding rectangle of all of the items in the quad-tree. For
            internal use only.
        """
        # The sub-quadrants are empty to start with.
        self.nw = self.ne = self.se = self.sw = None

        # If we've reached the maximum depth then insert all items into this
        # quadrant.
        depth -= 1
        if depth == 0:
            self.items = items
            return

        # Find this quadrant's centre.
        if bounding_rect:
            l, b, r, t = bounding_rect

        else:
            # If there isn't a bounding rect, then calculate it from the items.
            l = min(item.left for item in items)
            b = max(item.bottom for item in items)
            r = max(item.right for item in items)
            t = min(item.top for item in items)

        cx = self.cx = (l + r) * 0.5
        cy = self.cy = (t + b) * 0.5

        self.items = []
        nw_items = []
        ne_items = []
        se_items = []
        sw_items = []

        for item in items:
            # Which of the sub-quadrants does the item overlap?
            in_nw = item.left <= cx and item.top >= cy
            in_sw = item.left <= cx and item.bottom <= cy
            in_ne = item.right >= cx and item.top >= cy
            in_se = item.right >= cx and item.bottom <= cy

            # If it overlaps all 4 quadrants then insert it at the current
            # depth, otherwise append it to a list to be inserted under every
            # quadrant that it overlaps.
            if in_nw and in_ne and in_se and in_sw:
                self.items.append(item)
            else:
                if in_nw: nw_items.append(item)
                if in_ne: ne_items.append(item)
                if in_se: se_items.append(item)
                if in_sw: sw_items.append(item)

        # Create the sub-quadrants, recursively.
        if nw_items:
            self.nw = QuadTree(nw_items, depth, (l, cy, cx, t))
        if ne_items:
            self.ne = QuadTree(ne_items, depth, (cx, cy, r, t))
        if se_items:
            self.se = QuadTree(se_items, depth, (cx, b, r, cy))
        if sw_items:
            self.sw = QuadTree(sw_items, depth, (l, b, cx, cy))

    def hit(self, left_bottom_corner, right_top_corner):
        """Returns the items that overlap a bounding rectangle.

        Returns the set of all items in the quad-tree that overlap with a
        bounding rectangle.

        @param rect:
            The bounding rectangle being tested against the quad-tree. This
            must possess left, top, right and bottom attributes.
        """

        left = left_bottom_corner[0]
        bottom = left_bottom_corner[1]
        right = right_top_corner[0]
        top = right_top_corner[1]

        def overlaps(item):
            """https://developer.mozilla.org/en-US/docs/Games/Techniques/2D_collision_detection"""
            return (left <= item.right and
                   right >= item.left and
                    bottom <= item.top and
                    top >= item.bottom)


        # Find the hits at the current level.
        hits = set(item for item in self.items if overlaps(item))
        if len(hits) > 0:
            return True

        # Recursively check the lower quadrants.
        if self.nw and left <= self.cx and top >= self.cy:
            return self.nw.hit(left_bottom_corner, right_top_corner)
        if self.sw and left <= self.cx and bottom <= self.cy:
            return self.sw.hit(left_bottom_corner, right_top_corner)
        if self.ne and right >= self.cx and top >= self.cy:
            return self.ne.hit(left_bottom_corner, right_top_corner)
        if self.se and right >= self.cx and bottom <= self.cy:
            return self.se.hit(left_bottom_corner, right_top_corner)

        if len(hits) > 0:
            return True
        else:
            return False
