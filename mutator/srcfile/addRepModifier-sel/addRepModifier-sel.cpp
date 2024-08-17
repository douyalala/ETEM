//------------------------------------------------------------------------------
// mutate strategy: add or replace modifier
// inputs: targeted modifier unsigned, signed, short, long
// select positions that can mutate
// usage: addRepModifier-sel <path to main.c> --  <targeted modifier> <output dir>
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

static llvm::cl::OptionCategory VisitAST_Category("usage: addRepModifier-sel <path to main.c> --  <targeted modifier> <output dir>");
static string mutateType = "";
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
  string decl2str(VarDecl *d) {
    SourceLocation b(d->getSourceRange().getBegin()), _e(d->getSourceRange().getEnd());
    SourceLocation e(Lexer::getLocForEndOfToken(_e, 0, TheRewriter.getSourceMgr(), lopt));
    return string(TheRewriter.getSourceMgr().getCharacterData(b),
        TheRewriter.getSourceMgr().getCharacterData(e)-TheRewriter.getSourceMgr().getCharacterData(b));
  }

  bool VisitVarDecl(VarDecl *d) {
    if (!isa<ParmVarDecl>(d)) {
        // do not consider parameter decl
        // cout<<d->getType().getAsString()<<endl;
        if(strcmp(mutateType.c_str(),"unsigned")==0) {
            string identifier = mutateType;
            string inttype = "int";
            string chartype = "char";
            string shorttype = "short";
            string longtype = "long";
            string doubletype = "double";
            string oristr = decl2str(d);

            if(oristr.find(identifier) == string::npos 
                && (oristr.find(inttype) != string::npos 
                    || oristr.find(chartype) != string::npos 
                    || oristr.find(shorttype) != string::npos
                    || (oristr.find(longtype) != string::npos && oristr.find(doubletype) == string::npos))){
                // can mutate
                res_pos.push_back(d->getID());
            }
        } else if(strcmp(mutateType.c_str(),"signed")==0) {
            string identifier = mutateType;
            string inttype = "int";
            string chartype = "char";
            string shorttype = "short";
            string longtype = "long";
            string doubletype = "double";
            string signedtype = "unsigned";
            string oristr = decl2str(d);

            if((oristr.find(signedtype) != string::npos || oristr.find(identifier) == string::npos) 
                && (oristr.find(inttype) != string::npos 
                    || oristr.find(chartype) != string::npos 
                    || oristr.find(shorttype) != string::npos
                    || (oristr.find(longtype) != string::npos && oristr.find(doubletype) == string::npos))){
                // can mutate
                res_pos.push_back(d->getID());
            }

        } else if(strcmp(mutateType.c_str(),"short")==0) {
            string identifier = mutateType;
            string inttype = "int";
            string longtype = "long";
            string doubletype = "double";
            string oristr = decl2str(d);

            if((oristr.find(inttype) != string::npos 
                    || (oristr.find(longtype) != string::npos && oristr.find(doubletype) == string::npos))){
                // can mutate
                res_pos.push_back(d->getID());
            }

        } else if(strcmp(mutateType.c_str(),"long")==0) {
            string identifier = mutateType;
            string inttype = "int";
            string shorttype = "short";
            string oristr = decl2str(d);

            if((oristr.find(inttype) != string::npos 
                    || oristr.find(shorttype) != string::npos)){
                // can mutate
                res_pos.push_back(d->getID());
            }
        }    
    }

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
  mutateType = argv[3];
  output_dir = argv[4];

  cout<<"-- running: addRepModifier-sel"<<endl;
  cout<<"---- mutateType: "<<mutateType<<endl;
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
