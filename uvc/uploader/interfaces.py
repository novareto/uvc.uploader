from zope.interface import Interface
from zope import schema


class IDataChunk(Interface):
    """A chunk of data.
    """

    def __len__():
        """Returns the length of the data.
        """

    def __str__():
        """Returns the data.
        """


class INamedFile(Interface):
    """Defines a file that is aware of its filename.
    """
    filename = schema.TextLine(
        title=u"Name of file",
        required=True,
        default='',
        )

    contentType = schema.ASCIILine(
        title='Content Type',
        description='The content type identifies the type of data.',
        default='',
        required=False,
        missing_value='',
        )

    data = schema.Bytes(
        title='Data',
        description='The actual content of the object.',
        default=b'',
        missing_value=b'',
        required=False,
        )

    size = schema.Int(
        title='Size',
        description='Size in bytes',
        readonly=True,
        required=True,
        )
