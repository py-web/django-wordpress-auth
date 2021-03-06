from django.db import models

import phpserialize


class WpOptions(models.Model):
    option_id = models.BigIntegerField(primary_key=True)
    option_name = models.CharField(max_length=192, unique=True)
    option_value = models.TextField()
    autoload = models.CharField(max_length=60)

    class Meta:
        db_table = u'wp_options'

class WpUsermeta(models.Model):
    umeta_id = models.BigIntegerField(primary_key=True)
    user_id = models.BigIntegerField()
    meta_key = models.CharField(max_length=765, blank=True)
    meta_value = models.TextField(blank=True)

    class Meta:
        db_table = u'wp_usermeta'

class WpUsers(models.Model):
    # Field name made lowercase.
    id = models.BigIntegerField(primary_key=True, db_column='ID')

    login = models.CharField(max_length=180, db_column='user_login')
    password = models.CharField(max_length=192, db_column='user_pass')
    nicename = models.CharField(max_length=150, db_column='user_nicename')
    email = models.CharField(max_length=300, db_column='user_email')
    url = models.CharField(max_length=300, db_column='user_url')
    user_registered = models.DateTimeField(db_column='user_registered')
    user_activation_key = models.CharField(max_length=180,
                                           db_column='user_activation_key')
    user_status = models.IntegerField(db_column='user_status')
    display_name = models.CharField(max_length=750, db_column='display_name')

    class Meta:
        db_table = u'wp_users'

    def __str__(self):
        return str(self.login)

    @property
    def roles(self):
        """ Returns a list of all roles for the user. """
        php_serialized_roles = WpUsermeta.objects.using('wordpress').get(
            user_id=self.id, meta_key='wp_capabilities').meta_value
        roles = phpserialize.loads(php_serialized_roles)
        return [role for role, enabled in roles.iteritems() if enabled]

    @property
    def capabilities(self):
        capabilities = []
        roles_data = phpserialize.loads(
            WpOptions.objects.using('wordpress')\
            .get(option_name='wp_user_roles').option_value)
        for role in self.roles:
            role_capabilities = roles_data.get(role).get('capabilities')
            for capability, enabled in role_capabilities.iteritems():
                if enabled:
                    capabilities.append(capability)
        return set(capabilities)
