import orm
import typesystem


class ForeignKey(orm.ForeignKey):

    def get_validator(self, **kwargs) -> typesystem.Field:
        return self.ForeignKeyValidator(**kwargs)
