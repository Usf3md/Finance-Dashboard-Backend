from djoser.serializers import UserSerializer as BaseUserSerializezr


class UserSerializer(BaseUserSerializezr):
    class Meta(BaseUserSerializezr.Meta):
        fields = ['id', 'full_name', 'email', 'is_control']
