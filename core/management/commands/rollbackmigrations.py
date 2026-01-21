from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db.migrations.recorder import MigrationRecorder
from django.apps import apps

class Command(BaseCommand):
    help = "Rollback last N migrations for multiple apps in one command."

    def add_arguments(self, parser):
        parser.add_argument(
            "app_steps",
            type=str,
            help=(
                "Pass apps and steps as comma-separated list: "
                "app1:2,app2:1,app3:2"
            )
        )

    def handle(self, *args, **options):
        app_steps_str = options["app_steps"]
        app_steps_list = app_steps_str.split(",")

        for app_step in app_steps_list:
            try:
                app_name, steps_str = app_step.split(":")
                steps = int(steps_str)
            except ValueError:
                self.stdout.write(self.style.ERROR(
                    f"Invalid format for '{app_step}'. Use app:steps"
                ))
                continue

            # Validate app
            try:
                apps.get_app_config(app_name)
            except LookupError:
                self.stdout.write(self.style.ERROR(f"App '{app_name}' does not exist."))
                continue

            # Get applied migrations
            applied = (
                MigrationRecorder.Migration.objects
                .filter(app=app_name)
                .order_by("-applied")
            )

            count = applied.count()
            if count == 0:
                self.stdout.write(self.style.WARNING(f"No applied migrations for app '{app_name}'."))
                continue

            # Determine target migration
            if steps >= count:
                target_name = "zero"
            else:
                target_name = applied[steps].name

            last_applied = [m.name for m in applied[:steps]]

            self.stdout.write(self.style.SUCCESS(
                f"\nRolling back last {steps} migrations for '{app_name}':"
            ))
            for m in last_applied:
                self.stdout.write(f" - {m}")

            self.stdout.write(self.style.SUCCESS(f"Target migration → {target_name}"))

            # Run rollback
            call_command("migrate", app_name, target_name)
