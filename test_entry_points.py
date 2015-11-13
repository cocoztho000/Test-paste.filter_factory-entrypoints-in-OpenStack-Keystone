# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import stevedore
from testtools import matchers

import keystone
import keystone.middleware
from keystone.tests.unit import core as test
import oslo_middleware


class TestPasteDeploymentEntryPoints(test.TestCase):
    def test_entry_point_middleware(self):
        """Assert that our list of expected middleware is present."""
        expected_factory_module_class = {
            'admin_token_auth': {'project': 'keystone',
                                 'module_list':
                                 ['middleware',
                                  'AdminTokenAuthMiddleware']},

            'build_auth_context': {'project': 'keystone',
                                   'module_list':
                                     ['middleware',
                                      'AuthContextMiddleware']},

            'cors_extension': {'project': 'oslo_middleware',
                               'module_list': ['cors'],
                               'use_factory': False},

            'crud_extension': {'project': 'keystone',
                               'module_list': ['contrib',
                                               'admin_crud',
                                               'CrudExtension']},

            'debug': {'project': 'keystone',
                      'module_list': ['common',
                                      'wsgi',
                                      'Debug']},

            'endpoint_filter_extension': {'project': 'keystone',
                                          'module_list':
                                              ['contrib',
                                               'endpoint_filter',
                                               'routers',
                                               'EndpointFilterExtension']},

            'ec2_extension': {'project': 'keystone',
                              'module_list': ['contrib',
                                              'ec2',
                                              'Ec2Extension']},

            'ec2_extension_v3': {'project': 'keystone',
                                 'module_list': ['contrib',
                                                 'ec2',
                                                 'Ec2ExtensionV3']},

            'federation_extension': {'project': 'keystone',
                                     'module_list':
                                         ['contrib',
                                          'federation',
                                          'routers',
                                          'FederationExtension']},

            'json_body': {'project': 'keystone',
                          'module_list': ['middleware',
                                          'JsonBodyMiddleware']},

            'oauth1_extension': {'project': 'keystone',
                                 'module_list': ['contrib',
                                                 'oauth1',
                                                 'routers',
                                                 'OAuth1Extension']},

            'request_id': {'project': 'oslo_middleware',
                           'module_list': ['RequestId']},

            'revoke_extension': {'project': 'keystone',
                                 'module_list': ['contrib',
                                                 'revoke',
                                                 'routers',
                                                 'RevokeExtension']},

            's3_extension': {'project': 'keystone',
                             'module_list': ['contrib',
                                             's3',
                                             'S3Extension']},

            'simple_cert_extension': {'project': 'keystone',
                                      'module_list':
                                          ['contrib',
                                           'simple_cert',
                                           'SimpleCertExtension']},

            'sizelimit': {'project': 'oslo_middleware',
                          'module_list': ['sizelimit',
                                          'RequestBodySizeLimiter']},

            'token_auth': {'project': 'keystone',
                           'module_list': ['middleware',
                                           'TokenAuthMiddleware']},

            'url_normalize': {'project': 'keystone',
                              'module_list': ['middleware',
                                              'NormalizingFilter']},

            'user_crud_extension': {'project': 'keystone',
                                    'module_list': ['contrib',
                                                    'user_crud',
                                                    'CrudExtension']},
        }

        em = stevedore.ExtensionManager('paste.filter_factory')

        # Ensure all the factories are defined by their names
        factory_names = [extension.name for extension in em]
        self.assertThat(factory_names,
                        matchers.ContainsAll(expected_factory_module_class))

        for fact_name, fact_dict in expected_factory_module_class.items():
            # Get instance of factory from stevador
            e = [m for m in em if m.name == fact_name][0]

            # What project is the factory in
            _project = self._get_project(fact_dict['project'])
            # Get first instance of the factory
            _project_attr = getattr(_project, fact_dict['module_list'][0])

            # Get instance of the factory
            factory = self._get_attribute(
                fact_dict['module_list'][1:],
                _project_attr,
                use_factory=fact_dict.get('use_factory', True))
            self.assertEqual(factory, e.plugin)

    def _get_attribute(self, attr_list, factory_attribute, use_factory=False):
        """Recursivly go through the attribute list
        until you get to the factory
        """
        if not len(attr_list):
            if use_factory:
                return factory_attribute.factory
            else:
                return factory_attribute.filter_factory

        factory_attribute = getattr(factory_attribute, attr_list.pop(0))
        return self._get_attribute(attr_list, factory_attribute, use_factory)

    def _get_project(self, project):
        """Check which project the filter factory is
        from the origional instance
        """
        if project == 'keystone':
            return keystone
        elif project == 'keystone.middleware':
            return keystone.middleware
        elif project == 'oslo_middleware':
            return oslo_middleware
        return
