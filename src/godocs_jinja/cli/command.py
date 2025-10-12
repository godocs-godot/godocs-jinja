from argparse import ArgumentParser, Namespace
from typing import Any, cast
from godocs.cli.command import CLICommand
from godocs.parser import xml_parser, context_creator
from godocs.parser.context_creator import DocContext
from godocs.translation.interpreter import Interpreter, BBCodeInterpreter
from godocs.translation.translator import get_translator, SyntaxTranslator
from godocs_jinja.constructor import JinjaConstructor
from godocs.constructor.constructor import ConstructorContext


class JinjaCommand(CLICommand):
    """
    A `CLICommand` that allows defining the behavior of the
    `jinja_constructor`.
    """

    MODELS = ["rst"]
    """
    The default models accepted by this command.
    """

    parser: ArgumentParser
    """
    The `argparse.ArgumentParser` instance this `JinjaCommand` uses.
    """

    # TODO: move to dedicated place, and organize better
    def translate_ctx(self, ctx: DocContext, interpreter: Interpreter, translator: SyntaxTranslator):
        classes = ctx["classes"]
        for class_doc in classes:
            for member in class_doc:
                match(member):
                    case "brief_description":
                        class_doc[member] = interpreter.interpret(
                            class_doc[member]).translate(translator)
                    case "description":
                        class_doc[member] = interpreter.interpret(
                            class_doc[member]).translate(translator)
                    case "constants":
                        constants = class_doc[member]
                        for constant in constants:
                            constant["description"] = interpreter.interpret(
                                constant["description"]).translate(translator)
                    case "enums":
                        enums = class_doc[member]
                        for enum in enums:
                            enum["description"] = interpreter.interpret(
                                enum["description"]).translate(translator)
                            constants = enum["values"]
                            for constant in constants:
                                constant["description"] = interpreter.interpret(
                                    constant["description"]).translate(translator)
                    case "methods":
                        methods = class_doc[member]
                        for method in methods:
                            method["description"] = interpreter.interpret(
                                method["description"]).translate(translator)
                    case "properties":
                        properties = class_doc[member]
                        for property in properties:
                            property["description"] = interpreter.interpret(
                                property["description"]).translate(translator)
                    case "signals":
                        signals = class_doc[member]
                        for signal in signals:
                            signal["description"] = interpreter.interpret(
                                signal["description"]).translate(translator)
                    case "theme_items":
                        theme_items = class_doc[member]
                        for theme_item in theme_items:
                            theme_item["description"] = interpreter.interpret(
                                theme_item["description"]).translate(translator)
                    case _: pass

        return ctx

    def exec(self, args: Namespace):
        """
        Executes the main logic of this command with the parsed `args`.
        """

        docs = xml_parser.parse(args.input_dir)

        ctx = context_creator.create(docs)

        interpreter = BBCodeInterpreter()

        translator = get_translator(args.translator)

        ctx = self.translate_ctx(ctx, interpreter, translator)

        constructor = JinjaConstructor(
            model=args.model,
            templates_path=args.templates,
            filters_path=args.filters,
            # TODO: add builders path as option, so it can be passed here
            output_format="rst",  # TODO: make format customizable
        )

        constructor.construct(cast(ConstructorContext, ctx), args.output_dir)

    def register(self, subparsers: Any | None = None, parent: ArgumentParser | None = None):
        """
        Registers this `JinjaCommand` as a subparser for the
        `subparsers` received.
        """

        if subparsers is None:
            raise ValueError('subparsers is needed for "jinja" resistration')

        self.parser: ArgumentParser = subparsers.add_parser(
            "jinja", help="Construct docs using the Jinja constructor.", parents=[parent])

        self.parser.add_argument(
            "-m", "--model",
            default="rst",
            help=f"Which model to use. Can be one of {JinjaCommand.MODELS} or a path to a model directory."
        )
        self.parser.add_argument(
            "-T", "--templates",
            help="Path to directory with Jinja templates."
        )
        self.parser.add_argument(
            "-F", "--filters",
            help="Path to script with Jinja filter functions."
        )
        self.parser.add_argument(
            "-B", "--builders",
            help="Path to script with builders dict."
        )
        self.parser.set_defaults(func=self.exec)
