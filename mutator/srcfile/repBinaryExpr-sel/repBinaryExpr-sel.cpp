//------------------------------------------------------------------------------
// mutation strategy: replace binary operation
// inputs: oldOp and newOp
// select posisions that can mutate
// usage: repBinaryExpr-sel <path to main.c> --  <output dir>
//------------------------------------------------------------------------------
#include <sstream>
#include <string>
#include <iostream>
#include <fstream>
#include <memory>
#include <map>
#include <vector>
#include "clang/AST/AST.h"
#include "clang/AST/ASTConsumer.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/Frontend/ASTConsumers.h"
#include "clang/Frontend/FrontendActions.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"
#include "clang/Rewrite/Core/Rewriter.h"
#include "llvm/Support/raw_ostream.h"
#include "clang/Lex/Lexer.h"
using namespace std;
using namespace clang;
using namespace clang::driver;
using namespace clang::tooling;

static llvm::cl::OptionCategory VisitAST_Category("repBinaryExpr-sel <path to main.c> -- <output dir>");
static string output_dir = "";
static ofstream out;
static vector<int64_t> res_pos;

// By implementing RecursiveASTVisitor, we can specify which AST nodes
// we're interested in by overriding relevant methods.
class MyASTVisitor : public RecursiveASTVisitor<MyASTVisitor> {
public:
  ASTContext *Context=NULL;
  MyASTVisitor(Rewriter &R) : TheRewriter(R) {}
  LangOptions lopt;

  string stmt2str(Stmt *s) {
    SourceLocation b(s->getSourceRange().getBegin()), _e(s->getSourceRange().getEnd());
    SourceLocation e(Lexer::getLocForEndOfToken(_e, 0, TheRewriter.getSourceMgr(), lopt));
    return string(TheRewriter.getSourceMgr().getCharacterData(b),
        TheRewriter.getSourceMgr().getCharacterData(e)-TheRewriter.getSourceMgr().getCharacterData(b));
  }

  bool VisitBinaryOperator(BinaryOperator *b) {

    res_pos.push_back(b->getID(*Context));

    cout<<"------"<< b->getID(*Context) << endl;
    cout<<"pos: "<< b->getID(*Context) << endl;
    cout<<"BinaryOperator: "<< stmt2str(b) << endl;

    return true;
  }

private:
  Rewriter &TheRewriter;
};

// Implementation of the ASTConsumer interface for reading an AST produced
// by the Clang parser.
class MyASTConsumer : public ASTConsumer {
public:
  MyASTConsumer(Rewriter &R) : Visitor(R) {}

  void HandleTranslationUnit(ASTContext &Context) override  {
    /* we can use ASTContext to get the TranslationUnitDecl, which is
       a single Decl that collectively represents the entire source file */
    Visitor.Context=&Context;
    Visitor.TraverseDecl(Context.getTranslationUnitDecl());
  }

private:
  MyASTVisitor Visitor;
};

// For each source file provided to the tool, a new FrontendAction is created.
class MyFrontendAction : public ASTFrontendAction {
public:
  MyFrontendAction() {}

  void EndSourceFileAction() override {
    SourceManager &SM = TheRewriter.getSourceMgr();
    llvm::errs() << "** EndSourceFileAction for: "
                 << SM.getFileEntryForID(SM.getMainFileID())->getName() << "\n";
  }

  std::unique_ptr<ASTConsumer> CreateASTConsumer(CompilerInstance &CI,
                                                 StringRef file) override {
    llvm::errs() << "** Creating AST consumer for: " << file << "\n";
    TheRewriter.setSourceMgr(CI.getSourceManager(), CI.getLangOpts());
    return make_unique<MyASTConsumer>(TheRewriter);
  }

private:
  Rewriter TheRewriter;
};

int main(int argc, const char **argv) {
  srand( (unsigned)time( NULL ) );
  output_dir = argv[3];

  cout<<"-- running: repBinaryExpr-sel"<<endl;
  cout<<"---- output_dir: "<<output_dir<<endl;

  llvm::Expected<clang::tooling::CommonOptionsParser> OptionsParser=CommonOptionsParser::create(argc, argv, VisitAST_Category);
  ClangTool Tool(OptionsParser->getCompilations(), OptionsParser->getSourcePathList());

  Tool.run(newFrontendActionFactory<MyFrontendAction>().get());

  out.open(output_dir,ios::trunc);
  if(out.fail()){     
    llvm::errs() <<"Error: Fail to open the out file." << "\n";
    out.close();
    return 0; 
  }
  for(long unsigned int i=0;i<res_pos.size();i++){
    out<<res_pos[i]<<endl;
  }

  return 0;
}
