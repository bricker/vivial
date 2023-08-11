import { NextFunction, Request, Response, Router } from 'express';
import * as acorn from "acorn";
import { tsPlugin } from "acorn-typescript";
import { AcornParseClass } from 'acorn-typescript/lib/middleware.js';

export type TypeScriptRequestBody = {
    typescript: string
}

// TODO: look into acorn plugins

const parser = acorn.Parser.extend(tsPlugin());

export function InternalApiRouter(): Router {
    const router = Router();

    router.post('/parse', async (req: Request, res: Response, next: NextFunction) => {
    try {
        const { typescript } = <TypeScriptRequestBody>req.body;





        // const ast = acorn.extend(tsPlugin()).parse(typescript, {
        //     ecmaVersion: "latest",
        //     sourceType: "module",
        //     locations: true,
        // });







        // res.send(ast)
    } catch (e: unknown) {
        next(e);
    }
    });

    return router;
}
