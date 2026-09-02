
from typing import Any, List, Union

class QueueItem:

    def __init__(self, value):
        self.value = value
        self.forward = None
        self.backward = None

class MissingItemError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class PriorityQueue:
    """
    Priority Queue which assumes that each new item added is unique
    """
    def __init__(self):
        self._lookup = {}
        self._front = None
        self._back = None
        self._queue_len = 0


    def __len__(self):
        return self._queue_len

    def enqueue(self, enqueue: Union[List[Any], Any]):
        
        if isinstance(enqueue, list):
            # Build Queue Items
            enqueueItems = [QueueItem(x) for x in enqueue]

            # Add Items to Lookup and Configure Pointers
            nextItem = self._back if self._back is not None else QueueItem(None)

            # Fix Queue Pointers
            if self._queue_len == 0:
                self._front = enqueueItems[0]
            self._back = enqueueItems[-1]

            for item in enqueueItems:
                self._lookup[item.value] = item
                nextItem.backward = item

                item.forward = nextItem if nextItem.value is not None else None

                nextItem = item

            # Update Length
            self._queue_len += len(enqueueItems)

        else:
            # Build Single Queue Item
            qItem = QueueItem(enqueue)
            self._lookup[enqueue] = qItem

            if self._queue_len == 0:
                self._front = qItem
                self._back = qItem

            else:
                qItem.forward = self._back
                self._back.backward = qItem

            self._queue_len += 1

    def dequeue(self):
        retObj = self._front

        self._front = retObj.backward

        if retObj.backward is not None:
            retObj.backward.forward = None

        retVal = retObj.value
        self._lookup.pop(retVal)

        del retObj

        self._queue_len -= 1
        return retVal



    def bumpup(self, qItem):
        # Ensure item exists in the queue
        # Get itemObj
        if qItem not in self._lookup:
            raise Exception("Invalid key: Item not in queue")
        
        itemObj = self._lookup[qItem]

        # Ensure item is not already front
        if self._front == itemObj:
            return

        if self._back == itemObj:
            self._back = itemObj.forward
            self._back.backward = None

        # Cut obj out of current queue position -> stitch adjacent pointers
        if itemObj.backward is not None:
            itemObj.backward.forward = itemObj.forward

        if itemObj.forward is not None:
            itemObj.forward.backward = itemObj.backward

        # Put item at front of queue
        frontObj = self._front
        frontObj.forward = itemObj
        itemObj.forward = None
        itemObj.backward = frontObj

        # Set new queue front
        self._front = itemObj