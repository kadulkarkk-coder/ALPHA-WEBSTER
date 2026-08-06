"""
Configuration Validator
"""


class ConfigValidator:
    """
    Validates Webster configuration.
    """

    REQUIRED_KEYS = (

        "application",

        "version",

        "debug"

    )

    def validate(
        self,
        config: dict
    ) -> None:

        for key in self.REQUIRED_KEYS:

            if key not in config:

                raise ValueError(
                    f"Missing configuration key: {key}"
                )